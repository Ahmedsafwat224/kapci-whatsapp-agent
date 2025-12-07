"""
KAPCI WhatsApp AI Agent - Ticket Service
Ticket Management and Operations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import and_, or_

from app.models import (
    db, Ticket, Customer, Technician, TicketStatusHistory,
    TicketStatus, TechnicalDecision, CompensationType
)


class TicketService:
    """Ticket Management Service"""
    
    def create_ticket(self, customer_id: int, data: Dict) -> Ticket:
        """
        Create a new ticket
        
        Args:
            customer_id: Customer ID
            data: Ticket data
            
        Returns:
            Created ticket
        """
        ticket = Ticket(
            ticket_number=Ticket.generate_ticket_number(),
            customer_id=customer_id,
            product_name=data.get('product_name'),
            product_sku=data.get('product_sku'),
            purchase_date=data.get('purchase_date'),
            quantity=data.get('quantity', 1),
            issue_description=data.get('issue_description'),
            issue_category=data.get('issue_category'),
            photos=data.get('photos', []),
            status=TicketStatus.PENDING_REVIEW.value,
            priority=data.get('priority', 'normal')
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Log status change
        self._log_status_change(ticket.id, None, TicketStatus.PENDING_REVIEW.value, 'System', 'Ticket created')
        
        # Auto-assign technician
        self.assign_technician(ticket.id)
        
        return ticket
    
    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Get ticket by ID"""
        return Ticket.query.get(ticket_id)
    
    def get_ticket_by_number(self, ticket_number: str) -> Optional[Ticket]:
        """Get ticket by ticket number"""
        return Ticket.query.filter_by(ticket_number=ticket_number).first()
    
    def get_customer_tickets(self, customer_id: int, limit: int = 10) -> List[Ticket]:
        """Get tickets for a customer"""
        return Ticket.query.filter_by(customer_id=customer_id)\
            .order_by(Ticket.created_at.desc())\
            .limit(limit).all()
    
    def get_tickets_by_status(self, status: str) -> List[Ticket]:
        """Get tickets by status"""
        return Ticket.query.filter_by(status=status)\
            .order_by(Ticket.created_at.asc()).all()
    
    def get_pending_tickets(self) -> List[Ticket]:
        """Get all pending review tickets"""
        return Ticket.query.filter_by(status=TicketStatus.PENDING_REVIEW.value)\
            .order_by(Ticket.created_at.asc()).all()
    
    def get_technician_tickets(self, technician_id: int) -> List[Ticket]:
        """Get tickets assigned to a technician"""
        return Ticket.query.filter_by(assigned_technician_id=technician_id)\
            .filter(Ticket.status.in_([
                TicketStatus.PENDING_REVIEW.value,
                TicketStatus.UNDER_REVIEW.value
            ]))\
            .order_by(Ticket.created_at.asc()).all()
    
    def update_ticket(self, ticket_id: int, data: Dict) -> Optional[Ticket]:
        """
        Update ticket data
        
        Args:
            ticket_id: Ticket ID
            data: Update data
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        for key, value in data.items():
            if hasattr(ticket, key):
                setattr(ticket, key, value)
        
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        
        return ticket
    
    def update_status(self, ticket_id: int, new_status: str, 
                     changed_by: str = 'System', reason: str = None) -> Optional[Ticket]:
        """
        Update ticket status
        
        Args:
            ticket_id: Ticket ID
            new_status: New status
            changed_by: Who made the change
            reason: Reason for change
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()
        
        if new_status == TicketStatus.COMPLETED.value:
            ticket.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log status change
        self._log_status_change(ticket_id, old_status, new_status, changed_by, reason)
        
        return ticket
    
    def assign_technician(self, ticket_id: int, technician_id: int = None) -> Optional[Ticket]:
        """
        Assign ticket to technician
        
        Args:
            ticket_id: Ticket ID
            technician_id: Specific technician ID (optional, auto-assign if None)
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        if technician_id:
            technician = Technician.query.get(technician_id)
        else:
            # Auto-assign to technician with lowest workload
            technician = Technician.query.filter_by(is_active=True)\
                .filter(Technician.current_workload < Technician.max_workload)\
                .order_by(Technician.current_workload.asc())\
                .first()
        
        if technician:
            ticket.assigned_technician_id = technician.id
            technician.current_workload += 1
            db.session.commit()
            
            self._log_status_change(
                ticket_id, None, None, 'System',
                f'Assigned to technician: {technician.name}'
            )
        
        return ticket
    
    def record_technical_decision(self, ticket_id: int, decision: str,
                                  notes: str = None, technician_id: int = None) -> Optional[Ticket]:
        """
        Record technical team decision
        
        Args:
            ticket_id: Ticket ID
            decision: Decision (approved/rejected)
            notes: Technical notes
            technician_id: Technician who made decision
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        ticket.technical_decision = decision
        ticket.technical_notes = notes
        ticket.technical_review_date = datetime.utcnow()
        
        # Update technician workload
        if ticket.assigned_technician:
            ticket.assigned_technician.current_workload = max(
                0, ticket.assigned_technician.current_workload - 1
            )
        
        if decision == TechnicalDecision.REJECTED.value:
            ticket.status = TicketStatus.REJECTED.value
            changed_by = ticket.assigned_technician.name if ticket.assigned_technician else 'Technical Team'
            self._log_status_change(ticket_id, ticket.status, TicketStatus.REJECTED.value, 
                                   changed_by, f'Rejected: {notes}')
        else:
            # Route to compensation
            self.route_to_compensation(ticket_id)
        
        db.session.commit()
        return ticket
    
    def route_to_compensation(self, ticket_id: int) -> Optional[Ticket]:
        """
        Route approved ticket to appropriate compensation flow
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        customer = ticket.customer
        
        if customer and customer.has_kapci_account:
            # Customer has account - route to finance for refund
            ticket.compensation_type = CompensationType.REFUND.value
            ticket.status = TicketStatus.PENDING_FINANCE.value
            self._log_status_change(
                ticket_id, TicketStatus.APPROVED.value, 
                TicketStatus.PENDING_FINANCE.value,
                'System', 'Routed to Finance for refund'
            )
        else:
            # No account - route to inventory for replacement
            ticket.compensation_type = CompensationType.REPLACEMENT.value
            ticket.status = TicketStatus.PENDING_INVENTORY.value
            self._log_status_change(
                ticket_id, TicketStatus.APPROVED.value,
                TicketStatus.PENDING_INVENTORY.value,
                'System', 'Routed to Inventory for replacement'
            )
        
        db.session.commit()
        return ticket
    
    def process_finance_approval(self, ticket_id: int, sales_order: str = None) -> Optional[Ticket]:
        """
        Process finance department approval
        
        Args:
            ticket_id: Ticket ID
            sales_order: Sales order number
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        ticket.sales_order_number = sales_order
        ticket.status = TicketStatus.FINANCE_APPROVED.value
        
        self._log_status_change(
            ticket_id, TicketStatus.PENDING_FINANCE.value,
            TicketStatus.FINANCE_APPROVED.value,
            'Finance Team', f'Sales order created: {sales_order}'
        )
        
        db.session.commit()
        return ticket
    
    def process_inventory_preparation(self, ticket_id: int, tracking: str = None) -> Optional[Ticket]:
        """
        Process inventory department preparation
        
        Args:
            ticket_id: Ticket ID
            tracking: Replacement tracking number
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        ticket.replacement_tracking = tracking
        ticket.status = TicketStatus.INVENTORY_PREPARED.value
        
        self._log_status_change(
            ticket_id, TicketStatus.PENDING_INVENTORY.value,
            TicketStatus.INVENTORY_PREPARED.value,
            'Inventory Team', f'Replacement prepared. Tracking: {tracking}'
        )
        
        db.session.commit()
        return ticket
    
    def complete_ticket(self, ticket_id: int, completed_by: str = 'System') -> Optional[Ticket]:
        """
        Mark ticket as completed
        
        Args:
            ticket_id: Ticket ID
            completed_by: Who completed it
            
        Returns:
            Updated ticket
        """
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return None
        
        old_status = ticket.status
        ticket.status = TicketStatus.COMPLETED.value
        ticket.completed_at = datetime.utcnow()
        
        self._log_status_change(ticket_id, old_status, TicketStatus.COMPLETED.value,
                               completed_by, 'Ticket completed')
        
        db.session.commit()
        return ticket
    
    def get_overdue_tickets(self, days: int = 2) -> List[Ticket]:
        """
        Get tickets that have exceeded review time
        
        Args:
            days: Number of days threshold
            
        Returns:
            List of overdue tickets
        """
        threshold = datetime.utcnow() - timedelta(days=days)
        
        return Ticket.query.filter(
            and_(
                Ticket.status.in_([
                    TicketStatus.PENDING_REVIEW.value,
                    TicketStatus.UNDER_REVIEW.value
                ]),
                Ticket.created_at < threshold
            )
        ).order_by(Ticket.created_at.asc()).all()
    
    def get_statistics(self) -> Dict:
        """
        Get ticket statistics
        
        Returns:
            Statistics dictionary
        """
        total = Ticket.query.count()
        pending = Ticket.query.filter_by(status=TicketStatus.PENDING_REVIEW.value).count()
        approved = Ticket.query.filter(Ticket.technical_decision == TechnicalDecision.APPROVED.value).count()
        rejected = Ticket.query.filter_by(status=TicketStatus.REJECTED.value).count()
        completed = Ticket.query.filter_by(status=TicketStatus.COMPLETED.value).count()
        
        # This week
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_this_week = Ticket.query.filter(Ticket.created_at >= week_ago).count()
        
        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'completed': completed,
            'new_this_week': new_this_week,
            'pending_finance': Ticket.query.filter_by(status=TicketStatus.PENDING_FINANCE.value).count(),
            'pending_inventory': Ticket.query.filter_by(status=TicketStatus.PENDING_INVENTORY.value).count()
        }
    
    def _log_status_change(self, ticket_id: int, old_status: str, 
                          new_status: str, changed_by: str, reason: str = None):
        """Log ticket status change"""
        history = TicketStatusHistory(
            ticket_id=ticket_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason
        )
        db.session.add(history)
    
    def get_status_history(self, ticket_id: int) -> List[TicketStatusHistory]:
        """Get ticket status history"""
        return TicketStatusHistory.query.filter_by(ticket_id=ticket_id)\
            .order_by(TicketStatusHistory.created_at.asc()).all()


# Singleton instance
ticket_service = TicketService()
