"""
KAPCI WhatsApp AI Agent - API Routes
"""
from flask import Blueprint, request, jsonify, current_app
from app.models import db, Ticket, Customer, Technician, Conversation
from app.services import workflow_service, ticket_service, whatsapp_service

api = Blueprint('api', __name__, url_prefix='/api')


# ==========================================
# WHATSAPP WEBHOOK ROUTES
# ==========================================

@api.route('/webhook/whatsapp', methods=['GET'])
def verify_webhook():
    """Verify WhatsApp webhook subscription"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    result = whatsapp_service.verify_webhook(mode, token, challenge)
    
    if result:
        return result, 200
    return 'Forbidden', 403


@api.route('/webhook/whatsapp', methods=['POST'])
def receive_message():
    """Receive incoming WhatsApp message"""
    payload = request.json
    
    # Parse incoming message
    parsed = whatsapp_service.parse_incoming_message(payload)
    
    if not parsed:
        return jsonify({'status': 'no_message'}), 200
    
    # Process message
    try:
        response = workflow_service.handle_incoming_message(
            phone=parsed['from'],
            message=parsed.get('content', ''),
            message_type=parsed.get('type', 'text'),
            media_id=parsed.get('media_id'),
            contact_name=parsed.get('contact_name')
        )
        
        # Send response via WhatsApp
        whatsapp_service.send_text_message(parsed['from'], response)
        
        # Mark as read
        if parsed.get('message_id'):
            whatsapp_service.mark_as_read(parsed['message_id'])
        
        return jsonify({'status': 'processed'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error processing message: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==========================================
# CHAT DEMO ROUTES (for testing without WhatsApp)
# ==========================================

@api.route('/chat', methods=['POST'])
def chat():
    """Demo chat endpoint"""
    data = request.json
    phone = data.get('phone', '+20100000000')
    message = data.get('message', '')
    
    if not message.strip():
        return jsonify({'error': 'Empty message'}), 400
    
    try:
        response = workflow_service.handle_incoming_message(
            phone=phone,
            message=message,
            message_type='text'
        )
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/messages/<phone>', methods=['GET'])
def get_messages(phone):
    """Get chat history for a phone number"""
    customer = Customer.query.filter_by(phone_number=phone).first()
    
    if not customer:
        return jsonify({'messages': []})
    
    messages = Conversation.query.filter_by(customer_id=customer.id)\
        .order_by(Conversation.created_at.asc()).all()
    
    return jsonify({
        'messages': [m.to_dict() for m in messages]
    })


# ==========================================
# TICKET ROUTES
# ==========================================

@api.route('/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filters"""
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    
    query = Ticket.query
    
    if status:
        query = query.filter_by(status=status)
    
    tickets = query.order_by(Ticket.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'tickets': [t.to_dict() for t in tickets]
    })


@api.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get single ticket details"""
    ticket = ticket_service.get_ticket(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Include status history
    history = ticket_service.get_status_history(ticket_id)
    
    result = ticket.to_dict()
    result['status_history'] = [
        {
            'old_status': h.old_status,
            'new_status': h.new_status,
            'changed_by': h.changed_by,
            'reason': h.reason,
            'created_at': h.created_at.isoformat()
        } for h in history
    ]
    
    return jsonify(result)


@api.route('/tickets/<int:ticket_id>/decision', methods=['POST'])
def make_decision(ticket_id):
    """Technical team makes decision on ticket"""
    data = request.json
    decision = data.get('decision')  # 'approved' or 'rejected'
    reason = data.get('reason', '')
    technician_id = data.get('technician_id')
    
    if decision not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid decision'}), 400
    
    success, notification = workflow_service.handle_technical_decision(
        ticket_id=ticket_id,
        decision=decision,
        notes=reason,
        technician_id=technician_id
    )
    
    if not success:
        return jsonify({'error': notification}), 404
    
    ticket = ticket_service.get_ticket(ticket_id)
    
    return jsonify({
        'success': True,
        'ticket': ticket.to_dict(),
        'notification': notification
    })


@api.route('/tickets/<int:ticket_id>/complete', methods=['POST'])
def complete_ticket(ticket_id):
    """Mark ticket as completed"""
    data = request.json or {}
    completed_by = data.get('completed_by', 'System')
    
    ticket = ticket_service.complete_ticket(ticket_id, completed_by)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    return jsonify({
        'success': True,
        'ticket': ticket.to_dict()
    })


@api.route('/tickets/<int:ticket_id>/assign', methods=['POST'])
def assign_ticket(ticket_id):
    """Assign ticket to technician"""
    data = request.json or {}
    technician_id = data.get('technician_id')
    
    ticket = ticket_service.assign_technician(ticket_id, technician_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    return jsonify({
        'success': True,
        'ticket': ticket.to_dict()
    })


# ==========================================
# TECHNICIAN ROUTES
# ==========================================

@api.route('/technicians', methods=['GET'])
def get_technicians():
    """Get all technicians"""
    technicians = Technician.query.filter_by(is_active=True).all()
    
    return jsonify({
        'technicians': [t.to_dict() for t in technicians]
    })


@api.route('/technicians/<int:tech_id>/tickets', methods=['GET'])
def get_technician_tickets(tech_id):
    """Get tickets assigned to a technician"""
    tickets = ticket_service.get_technician_tickets(tech_id)
    
    return jsonify({
        'tickets': [t.to_dict() for t in tickets]
    })


# ==========================================
# STATISTICS ROUTES
# ==========================================

@api.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    stats = ticket_service.get_statistics()
    return jsonify(stats)


@api.route('/stats/overdue', methods=['GET'])
def get_overdue():
    """Get overdue tickets"""
    days = request.args.get('days', 2, type=int)
    tickets = ticket_service.get_overdue_tickets(days)
    
    return jsonify({
        'count': len(tickets),
        'tickets': [t.to_dict() for t in tickets]
    })


# ==========================================
# CUSTOMER ROUTES
# ==========================================

@api.route('/customers/<phone>', methods=['GET'])
def get_customer(phone):
    """Get customer by phone number"""
    customer = Customer.query.filter_by(phone_number=phone).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify(customer.to_dict())


@api.route('/customers/<phone>/tickets', methods=['GET'])
def get_customer_tickets(phone):
    """Get tickets for a customer"""
    customer = Customer.query.filter_by(phone_number=phone).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    tickets = ticket_service.get_customer_tickets(customer.id)
    
    return jsonify({
        'customer': customer.to_dict(),
        'tickets': [t.to_dict() for t in tickets]
    })
