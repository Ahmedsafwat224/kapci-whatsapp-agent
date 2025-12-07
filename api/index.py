"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///kapci.db')

from app import create_app

app = create_app('production')

# Vercel expects the app to be named 'app' or 'handler'
# This is the WSGI application
