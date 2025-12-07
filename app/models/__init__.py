"""
KAPCI WhatsApp AI Agent - Database Models
"""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
import random
import string

db = SQLAlchemy()


# ==========================================
# ENUMS
# ==========================================

class TicketStatus(str, Enum):
    PENDING_DATA = 'pending_data'
    PENDING_REVIEW = 'pending_review'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING_FINANCE = 'pending_finance'
    FINANCE_APPROVED = 'finance_approved'
    PENDING_INVENTORY = 'pending_inventory'
    INVENTORY_PREPARED = 'inventory_prepared'
    IN_DELIVERY = 'in_delivery'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class TechnicalDecision(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class CompensationType(str, Enum):
    REFUND = 'refund'
    REPLACEMENT = 'replacement'


class ConversationStep(str, Enum):
    IDLE = 'idle'
    GREETING = 'greeting'
    COLLECTING_NAME = 'collecting_name'
    COLLECTING_PRODUCT = 'collecting_product'
    COLLECTING_PURCHASE_DATE = 'collecting_purchase_date'
    COLLECTING_QUANTITY = 'collecting_quantity'
    COLLECTING_ISSUE = 'collecting_issue'
    COLLECTING_PHOTOS = 'collecting_photos'
    CONFIRMING_DATA = 'confirming_data'
    AWAITING_RESPONSE = 'awaiting_response'


# ==========================================
# MODELS
# ==========================================

class Customer(db.Model):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    has_kapci_account = db.Column(db.Boolean, default=False)
    kapci_account_id = db.Column(db.String(50))
    preferred_language = db.Column(db.String(10), default='ar')  # ar, en
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='customer', lazy='dynamic')
    conversations = db.relationship('Conversation', backref='customer', lazy='dynamic')
    conversation_state = db.relationship('ConversationState', backref='customer', uselist=False)
    
    def __repr__(self):
        return f'<Customer {self.phone_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'customer_name': self.customer_name,
            'email': self.email,
            'has_kapci_account': self.has_kapci_account,
            'kapci_account_id': self.kapci_account_id,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Ticket(db.Model):
    """Ticket model for compensation requests"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Product Information
    product_name = db.Column(db.String(200))
    product_sku = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, default=1)
    
    # Issue Details
    issue_description = db.Column(db.Text)
    issue_category = db.Column(db.String(50))
    photos = db.Column(db.JSON)  # List of photo URLs/paths
    
    # Status and Workflow
    status = db.Column(db.String(30), default=TicketStatus.PENDING_DATA.value)
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    
    # Technical Review
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('technicians.id'))
    technical_decision = db.Column(db.String(20), default=TechnicalDecision.PENDING.value)
    technical_notes = db.Column(db.Text)
    technical_review_date = db.Column(db.DateTime)
    
    # Compensation
    compensation_type = db.Column(db.String(20))
    compensation_amount = db.Column(db.Numeric(10, 2))
    
    # Finance/Inventory
    sales_order_number = db.Column(db.String(50))
    replacement_tracking = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    status_history = db.relationship('TicketStatusHistory', backref='ticket', lazy='dynamic')
    
    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'
    
    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number: TKT-YYYY-XXXXX"""
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=5))
        return f"TKT-{year}-{random_part}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_number': self.ticket_number,
            'customer_id': self.customer_id,
            'customer_phone': self.customer.phone_number if self.customer else None,
            'customer_name': self.customer.customer_name if self.customer else None,
            'customer_has_account': self.customer.has_kapci_account if self.customer else False,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'quantity': self.quantity,
            'issue_description': self.issue_description,
            'issue_category': self.issue_category,
            'photos': self.photos,
            'status': self.status,
            'priority': self.priority,
            'technical_decision': self.technical_decision,
            'technical_notes': self.technical_notes,
            'compensation_type': self.compensation_type,
            'assigned_technician': self.assigned_technician.name if self.assigned_technician else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Technician(db.Model):
    """Technician model"""
    __tablename__ = 'technicians'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    
    is_active = db.Column(db.Boolean, default=True)
    current_workload = db.Column(db.Integer, default=0)
    max_workload = db.Column(db.Integer, default=10)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='assigned_technician', lazy='dynamic')
    
    def __repr__(self):
        return f'<Technician {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'is_active': self.is_active,
            'current_workload': self.current_workload,
            'max_workload': self.max_workload
        }


class Conversation(db.Model):
    """Conversation/Message history model"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(100), unique=True)  # WhatsApp message ID
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    
    direction = db.Column(db.String(10), nullable=False)  # inbound, outbound
    message_type = db.Column(db.String(20), default='text')  # text, image, document
    content = db.Column(db.Text)
    media_url = db.Column(db.String(500))
    
    intent = db.Column(db.String(50))  # Detected intent
    entities = db.Column(db.JSON)  # Extracted entities
    
    status = db.Column(db.String(20), default='sent')  # sent, delivered, read, failed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'content': self.content,
            'message_type': self.message_type,
            'intent': self.intent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConversationState(db.Model):
    """Track conversation state for each customer"""
    __tablename__ = 'conversation_states'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=True, nullable=False)
    
    current_step = db.Column(db.String(50), default=ConversationStep.IDLE.value)
    current_ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    collected_data = db.Column(db.JSON, default=dict)
    context = db.Column(db.JSON, default=dict)  # Additional context
    
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConversationState customer={self.customer_id} step={self.current_step}>'
    
    def reset(self):
        """Reset conversation state"""
        self.current_step = ConversationStep.IDLE.value
        self.current_ticket_id = None
        self.collected_data = {}
        self.context = {}
        self.session_start = datetime.utcnow()


class TicketStatusHistory(db.Model):
    """Track all status changes for audit"""
    __tablename__ = 'ticket_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    changed_by = db.Column(db.String(100))  # User/System who made the change
    reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketStatusHistory {self.ticket_id}: {self.old_status} -> {self.new_status}>'


class Notification(db.Model):
    """Notification tracking"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    
    notification_type = db.Column(db.String(50), nullable=False)
    channel = db.Column(db.String(20), default='whatsapp')  # whatsapp, email, sms
    content = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, failed
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'


class AdminUser(db.Model):
    """Admin/Staff users"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    role = db.Column(db.String(20), default='staff')  # admin, manager, staff, technician
    department = db.Column(db.String(50))
    
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db(app):
    """Initialize database and create tables"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Create default technician if none exists
        if not Technician.query.first():
            default_tech = Technician(
                employee_id='TECH001',
                name='Ahmed Mohamed',
                email='ahmed@kapci.com',
                department='Technical Support',
                is_active=True,
                max_workload=15
            )
            db.session.add(default_tech)
            
            tech2 = Technician(
                employee_id='TECH002',
                name='Sara Ali',
                email='sara@kapci.com',
                department='Technical Support',
                is_active=True,
                max_workload=15
            )
            db.session.add(tech2)
            db.session.commit()
        
        print("Database initialized successfully!")
