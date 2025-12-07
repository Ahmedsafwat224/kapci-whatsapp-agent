# KAPCI WhatsApp AI Agent

## 🎯 Overview

A comprehensive WhatsApp-based AI agent for automating KAPCI's product compensation and ticketing system. This system handles customer complaints via WhatsApp, processes compensation requests, and manages the complete workflow from complaint submission to resolution.

## ✨ Features

- **🤖 AI-Powered Chat**: Intelligent conversation handling with intent classification
- **🌐 Bilingual Support**: Full Arabic and English language support
- **📱 WhatsApp Integration**: Native WhatsApp Business API integration
- **🎫 Ticket Management**: Automated ticket creation and tracking
- **👨‍🔧 Technical Review**: Dashboard for technical team evaluation
- **💰 Smart Routing**: Automatic compensation routing (refund vs replacement)
- **📊 Analytics Dashboard**: Real-time statistics and insights
- **🔔 Notifications**: Automated customer notifications

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
python run.py
```

### Access Points

| Interface | URL | Description |
|-----------|-----|-------------|
| Chat Demo | http://localhost:5000 | WhatsApp-like chat interface |
| Admin Dashboard | http://localhost:5000/admin | Technical team dashboard |
| Technician Portal | http://localhost:5000/technician | Technician workstation |
| Analytics | http://localhost:5000/dashboard | Statistics and charts |

## 📱 Chat Flow

```
Customer: "مرحبا" (Hello)
Bot: Welcome message with menu

Customer: "1" (New Complaint)
Bot: Request product information

Customer: "KAPCI Paint 5L, bought yesterday"
Bot: Request issue description

Customer: "Paint is too thick"
Bot: Request photos (optional)

Customer: "skip"
Bot: Show summary, request confirmation

Customer: "yes"
Bot: Ticket created! TKT-2024-12345
```

## 📁 Project Structure

```
kapci_full/
├── app/
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── routes/          # API endpoints
│   └── utils/           # Utilities
├── templates/           # HTML templates
├── static/              # Static files
├── config/              # Configuration
├── tests/               # Test suite
├── run.py               # Entry point
└── requirements.txt
```

## 🔌 API Endpoints

### Chat
- `POST /api/chat` - Send message and get response
- `GET /api/messages/<phone>` - Get chat history

### Tickets
- `GET /api/tickets` - List all tickets
- `POST /api/tickets/<id>/decision` - Make decision
- `POST /api/tickets/<id>/complete` - Complete ticket

### Statistics
- `GET /api/stats` - Get statistics

## 🧪 Testing

```bash
pytest tests/ -v
```

## 🚢 Production Deployment

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📝 License

Copyright © 2024 KAPCI. All rights reserved.
