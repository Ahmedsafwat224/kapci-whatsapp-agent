from flask import Flask, request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vercel-secret-key')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>KAPCI WhatsApp AI Agent</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; margin-bottom: 10px; }
            .status { background: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0; color: #065f46; }
            .links { margin-top: 20px; }
            .links a { display: inline-block; margin: 5px 10px 5px 0; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }
            .links a:hover { background: #1d4ed8; }
            .note { background: #fef3c7; padding: 15px; border-radius: 5px; margin-top: 20px; color: #92400e; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KAPCI WhatsApp AI Agent</h1>
            <p>Compensation Ticketing System</p>
            <div class="status">Server is running on Vercel!</div>
            <div class="links">
                <a href="/api/health">Health Check</a>
                <a href="/api/stats">Statistics</a>
            </div>
            <div class="note">
                <strong>Note:</strong> This is a serverless deployment. For full functionality with the chat interface and database, deploy using Docker or a traditional server.
            </div>
        </div>
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
    if request.method == 'GET':
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'kapci_verify_token')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        return 'Verification failed', 403

    return {'status': 'received'}, 200

@app.route('/favicon.ico')
def favicon():
    return '', 204
