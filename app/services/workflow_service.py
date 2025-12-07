"""
KAPCI WhatsApp AI Agent - Workflow Service
Main Conversation Orchestrator and State Machine
"""
from datetime import datetime
from typing import Dict, Optional, Tuple
import json

from app.models import (
    db, Customer, Ticket, Conversation, ConversationState,
    ConversationStep, TicketStatus
)
from app.services.ai_service import ai_service
from app.services.ticket_service import ticket_service
from app.services.whatsapp_service import whatsapp_service
from app.services.templates import MessageTemplates


class WorkflowService:
    """Main Workflow Orchestrator"""
    
    def __init__(self):
        self.templates = MessageTemplates()
    
    def handle_incoming_message(self, phone: str, message: str, 
                               message_type: str = 'text',
                               media_id: str = None,
                               contact_name: str = None) -> str:
        """
        Main entry point for handling incoming messages
        
        Args:
            phone: Customer phone number
            message: Message content
            message_type: Type of message (text, image, etc.)
            media_id: Media ID if applicable
            contact_name: Contact name from WhatsApp
            
        Returns:
            Response message to send
        """
        # Get or create customer
        customer = self._get_or_create_customer(phone, contact_name)
        
        # Get or create conversation state
        state = self._get_conversation_state(customer.id)
        
        # Save incoming message
        self._save_message(customer.id, 'inbound', message, message_type)
        
        # Detect language
        language = ai_service.detect_language(message)
        if language != customer.preferred_language:
            customer.preferred_language = language
            db.session.commit()
        
        # Classify intent
        intent = ai_service.classify_intent(message, state.current_step)
        
        # Extract entities
        entities = ai_service.extract_entities(message)
        
        # Route and process message
        response = self._route_message(customer, state, intent, message, entities, message_type, media_id)
        
        # Save outgoing message
        self._save_message(customer.id, 'outbound', response)
        
        # Update last message timestamp
        state.last_message_at = datetime.utcnow()
        db.session.commit()
        
        return response
    
    def _route_message(self, customer: Customer, state: ConversationState,
                      intent: str, message: str, entities: Dict,
                      message_type: str = 'text', media_id: str = None) -> str:
        """Route message based on state and intent"""
        
        current_step = state.current_step
        collected_data = state.collected_data or {}
        lang = customer.preferred_language
        
        # =========================================
        # IDLE STATE
        # =========================================
        if current_step == ConversationStep.IDLE.value:
            if intent == 'greeting':
                return self.templates.get_greeting(lang)
            
            elif intent == 'new_complaint':
                state.current_step = ConversationStep.COLLECTING_PRODUCT.value
                state.collected_data = {}
                db.session.commit()
                return self.templates.get_ask_product(lang)
            
            elif intent == 'check_status':
                return self._handle_status_check(customer, entities, lang)
            
            elif intent == 'help':
                return self.templates.get_help(lang)
            
            elif intent == 'thanks':
                return self.templates.get_thanks_response(lang)
            
            else:
                return self.templates.get_greeting(lang)
        
        # =========================================
        # COLLECTING PRODUCT INFO
        # =========================================
        elif current_step == ConversationStep.COLLECTING_PRODUCT.value:
            collected_data['product_name'] = message
            state.collected_data = collected_data
            state.current_step = ConversationStep.COLLECTING_ISSUE.value
            db.session.commit()
            return self.templates.get_ask_issue(lang)
        
        # =========================================
        # COLLECTING ISSUE DESCRIPTION
        # =========================================
        elif current_step == ConversationStep.COLLECTING_ISSUE.value:
            collected_data['issue_description'] = message
            collected_data['issue_category'] = ai_service.suggest_issue_category(message)
            state.collected_data = collected_data
            state.current_step = ConversationStep.COLLECTING_PHOTOS.value
            db.session.commit()
            return self.templates.get_ask_photos(lang)
        
        # =========================================
        # COLLECTING PHOTOS
        # =========================================
        elif current_step == ConversationStep.COLLECTING_PHOTOS.value:
            if intent == 'skip':
                collected_data['photos'] = []
            elif message_type == 'image' and media_id:
                photos = collected_data.get('photos', [])
                photos.append(media_id)
                collected_data['photos'] = photos
            else:
                collected_data['photos'] = []
            
            state.collected_data = collected_data
            state.current_step = ConversationStep.CONFIRMING_DATA.value
            db.session.commit()
            
            return self.templates.get_confirm_data(
                collected_data.get('product_name', '-'),
                collected_data.get('issue_description', '-'),
                lang
            )
        
        # =========================================
        # CONFIRMING DATA
        # =========================================
        elif current_step == ConversationStep.CONFIRMING_DATA.value:
            if intent == 'confirm_yes':
                # Create ticket
                ticket = ticket_service.create_ticket(customer.id, {
                    'product_name': collected_data.get('product_name'),
                    'issue_description': collected_data.get('issue_description'),
                    'issue_category': collected_data.get('issue_category'),
                    'photos': collected_data.get('photos', [])
                })
                
                # Reset state
                state.current_step = ConversationStep.IDLE.value
                state.collected_data = {}
                state.current_ticket_id = ticket.id
                db.session.commit()
                
                return self.templates.get_ticket_created(ticket.ticket_number, lang)
            
            elif intent == 'confirm_no':
                # Restart collection
                state.current_step = ConversationStep.COLLECTING_PRODUCT.value
                state.collected_data = {}
                db.session.commit()
                return self.templates.get_restart(lang) + "\n\n" + self.templates.get_ask_product(lang)
            
            else:
                return self.templates.get_confirm_prompt(lang)
        
        # =========================================
        # CANCEL
        # =========================================
        if intent == 'cancel':
            state.reset()
            db.session.commit()
            return self.templates.get_cancelled(lang)
        
        # =========================================
        # DEFAULT
        # =========================================
        return self.templates.get_unknown(lang)
    
    def _handle_status_check(self, customer: Customer, entities: Dict, lang: str) -> str:
        """Handle ticket status check request"""
        
        # Check if specific ticket number provided
        ticket_number = entities.get('ticket_number')
        
        if ticket_number:
            ticket = ticket_service.get_ticket_by_number(ticket_number)
        else:
            # Get latest ticket for customer
            tickets = ticket_service.get_customer_tickets(customer.id, limit=1)
            ticket = tickets[0] if tickets else None
        
        if ticket:
            return self.templates.get_ticket_status(ticket, lang)
        else:
            return self.templates.get_no_tickets(lang)
    
    def handle_technical_decision(self, ticket_id: int, decision: str, 
                                 notes: str = None, technician_id: int = None) -> Tuple[bool, str]:
        """
        Handle technical team decision and notify customer
        
        Args:
            ticket_id: Ticket ID
            decision: Decision (approved/rejected)
            notes: Technical notes
            technician_id: Technician ID
            
        Returns:
            Tuple of (success, notification_message)
        """
        ticket = ticket_service.record_technical_decision(ticket_id, decision, notes, technician_id)
        
        if not ticket:
            return False, "Ticket not found"
        
        customer = ticket.customer
        lang = customer.preferred_language if customer else 'ar'
        
        if decision == 'rejected':
            notification = self.templates.get_ticket_rejected(
                ticket.ticket_number, notes or 'No issue found', lang
            )
        else:
            if ticket.compensation_type == 'refund':
                notification = self.templates.get_ticket_approved_refund(ticket.ticket_number, lang)
            else:
                notification = self.templates.get_ticket_approved_replacement(ticket.ticket_number, lang)
        
        # Send WhatsApp notification (if configured)
        if customer and customer.phone_number:
            try:
                whatsapp_service.send_text_message(customer.phone_number, notification)
            except:
                pass  # Log error but don't fail
        
        # Save notification as message
        if customer:
            self._save_message(customer.id, 'outbound', notification)
        
        return True, notification
    
    def send_reminder(self, ticket_id: int, reminder_type: str) -> bool:
        """
        Send reminder notification
        
        Args:
            ticket_id: Ticket ID
            reminder_type: Type of reminder
            
        Returns:
            Success status
        """
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket or not ticket.customer:
            return False
        
        customer = ticket.customer
        lang = customer.preferred_language
        
        message = self.templates.get_reminder(ticket.ticket_number, reminder_type, lang)
        
        if customer.phone_number:
            try:
                whatsapp_service.send_text_message(customer.phone_number, message)
                self._save_message(customer.id, 'outbound', message)
                return True
            except:
                return False
        
        return False
    
    def _get_or_create_customer(self, phone: str, name: str = None) -> Customer:
        """Get existing customer or create new one"""
        customer = Customer.query.filter_by(phone_number=phone).first()
        
        if not customer:
            # For demo, randomly assign account status
            import random
            customer = Customer(
                phone_number=phone,
                customer_name=name,
                has_kapci_account=random.choice([True, False]),
                preferred_language='ar'
            )
            db.session.add(customer)
            db.session.commit()
        elif name and not customer.customer_name:
            customer.customer_name = name
            db.session.commit()
        
        return customer
    
    def _get_conversation_state(self, customer_id: int) -> ConversationState:
        """Get or create conversation state"""
        state = ConversationState.query.filter_by(customer_id=customer_id).first()
        
        if not state:
            state = ConversationState(
                customer_id=customer_id,
                current_step=ConversationStep.IDLE.value,
                collected_data={}
            )
            db.session.add(state)
            db.session.commit()
        
        return state
    
    def _save_message(self, customer_id: int, direction: str, 
                     content: str, message_type: str = 'text'):
        """Save message to conversation history"""
        message = Conversation(
            customer_id=customer_id,
            direction=direction,
            content=content,
            message_type=message_type
        )
        db.session.add(message)
        db.session.commit()


# Singleton instance
workflow_service = WorkflowService()
