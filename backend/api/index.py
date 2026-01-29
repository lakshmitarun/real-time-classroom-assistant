"""
Vercel WSGI entry point for Flask application
This file is required for Vercel to properly run the Flask app
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export the Flask app for Vercel
export = app
