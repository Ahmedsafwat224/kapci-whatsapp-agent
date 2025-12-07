"""
KAPCI WhatsApp AI Agent - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'kapci-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///kapci.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # WhatsApp Business API
    WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
    WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'kapci_verify_token')
    
    # External APIs
    CRM_API_URL = os.getenv('CRM_API_URL', 'http://localhost:8001/api')
    CRM_API_KEY = os.getenv('CRM_API_KEY', '')
    
    ERP_API_URL = os.getenv('ERP_API_URL', 'http://localhost:8002/api')
    ERP_API_KEY = os.getenv('ERP_API_KEY', '')
    
    INVENTORY_API_URL = os.getenv('INVENTORY_API_URL', 'http://localhost:8003/api')
    INVENTORY_API_KEY = os.getenv('INVENTORY_API_KEY', '')
    
    # AI/LLM Settings
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'local')  # local, openai, ollama
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama2')
    LLM_API_URL = os.getenv('LLM_API_URL', 'http://localhost:11434/api')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Business Rules
    TECHNICAL_REVIEW_MAX_DAYS = 2
    REFUND_PROCESSING_DAYS = 5
    REPLACEMENT_DELIVERY_DAYS = 3
    
    # Notification Settings
    ADMIN_NOTIFICATION_EMAILS = os.getenv('ADMIN_EMAILS', '').split(',')
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # Use environment variable or SQLite fallback for serverless
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///kapci.db'
    )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
