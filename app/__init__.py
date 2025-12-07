"""
KAPCI WhatsApp AI Agent - Application Factory
"""
import os
from flask import Flask
from config.settings import config


def create_app(config_name=None):
    """Application factory"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from app.models import db, init_db
    db.init_app(app)
    
    # Initialize services
    from app.services.whatsapp_service import whatsapp_service
    whatsapp_service.init_app(app)
    
    # Register blueprints
    from app.routes import api, web
    app.register_blueprint(api)
    app.register_blueprint(web)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default data
        from app.models import Technician
        if not Technician.query.first():
            tech1 = Technician(
                employee_id='TECH001',
                name='Ahmed Mohamed',
                email='ahmed@kapci.com',
                department='Technical Support',
                is_active=True,
                max_workload=15
            )
            tech2 = Technician(
                employee_id='TECH002',
                name='Sara Ali',
                email='sara@kapci.com',
                department='Technical Support',
                is_active=True,
                max_workload=15
            )
            tech3 = Technician(
                employee_id='TECH003',
                name='Mohamed Hassan',
                email='mohamed@kapci.com',
                department='Technical Support',
                is_active=True,
                max_workload=15
            )
            db.session.add_all([tech1, tech2, tech3])
            db.session.commit()
    
    return app
