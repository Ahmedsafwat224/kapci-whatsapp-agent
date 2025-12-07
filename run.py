#!/usr/bin/env python3
"""
KAPCI WhatsApp AI Agent - Main Entry Point
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("\n" + "="*60)
    print("  KAPCI WhatsApp AI Agent - Compensation Ticketing System")
    print("="*60)
    print(f"\n  🌐 Chat Interface:     http://localhost:{port}")
    print(f"  🔧 Admin Dashboard:    http://localhost:{port}/admin")
    print(f"  📊 Analytics:          http://localhost:{port}/dashboard")
    print(f"  👨‍🔧 Technician Portal: http://localhost:{port}/technician")
    print(f"\n  📡 WhatsApp Webhook:   http://localhost:{port}/api/webhook/whatsapp")
    print(f"  📚 API Base URL:       http://localhost:{port}/api")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
