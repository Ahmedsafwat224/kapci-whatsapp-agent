"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set environment variables for Vercel (before any imports)
os.environ['FLASK_ENV'] = 'production'

# Use in-memory SQLite for Vercel (serverless has no persistent filesystem)
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Now import Flask app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a minimal Flask app for Vercel
app = Flask(__name__,
            template_folder=os.path.join(project_root, 'templates'),
            static_folder=os.path.join(project_root, 'static'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vercel-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Simple health check route
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>KAPCI WhatsApp AI Agent</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2563eb; }
            .status { background: #d1fae5; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .links a { display: block; margin: 10px 0; color: #2563eb; }
        </style>
    </head>
    <body>
        <h1>KAPCI WhatsApp AI Agent</h1>
        <div class="status">✅ Server is running on Vercel!</div>
        <div class="links">
            <h3>Available Endpoints:</h3>
            <a href="/api/health">/api/health - Health Check</a>
            <a href="/api/stats">/api/stats - Statistics</a>
        </div>
        <p><strong>Note:</strong> This is a serverless deployment. For full functionality with database persistence, use a managed database like Vercel Postgres or Supabase.</p>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return {'status': 'healthy', 'message': 'KAPCI WhatsApp AI Agent is running on Vercel'}

@app.route('/api/stats')
def stats():
    return {
        'total_tickets': 0,
        'pending_review': 0,
        'completed_today': 0,
        'message': 'Demo mode - connect a database for real data'
    }

@app.route('/api/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    from flask import request

    # Webhook verification (GET request from WhatsApp)
    if request.method == 'GET':
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'kapci_verify_token')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        return 'Verification failed', 403

    # Handle incoming messages (POST request)
    return {'status': 'received'}, 200

# Required for Vercel
handler = app
