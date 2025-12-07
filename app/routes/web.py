"""
KAPCI WhatsApp AI Agent - Web Routes
Frontend Views and Pages
"""
from flask import Blueprint, render_template

web = Blueprint('web', __name__)


@web.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')


@web.route('/admin')
def admin():
    """Admin dashboard"""
    return render_template('admin.html')


@web.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return render_template('dashboard.html')


@web.route('/technician')
def technician_portal():
    """Technician portal"""
    return render_template('technician.html')
