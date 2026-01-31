import os
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# ============================================
# PRODUCTION VERCEL CORS CONFIGURATION
# ============================================

def setup_cors(app):
    """Setup CORS middleware for production Vercel deployment"""
    
    # Get frontend URL from environment
    FRONTEND_URLS = [
        # Development
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Add production URLs
    frontend_url = os.getenv('FRONTEND_URL', '')
    if frontend_url:
        FRONTEND_URLS.append(frontend_url)
    
    # Add any additional URLs from environment variable
    if os.getenv('ALLOWED_ORIGINS'):
        additional_urls = [url.strip() for url in os.getenv('ALLOWED_ORIGINS', '').split(',')]
        FRONTEND_URLS.extend(additional_urls)
    
    # Remove duplicates and empty strings
    FRONTEND_URLS = [url.strip() for url in set(FRONTEND_URLS) if url.strip()]
    
    logger.info(f"[CORS] Allowed origins: {FRONTEND_URLS}")
    
    def is_origin_allowed(origin):
        """Check if origin is allowed for CORS"""
        if not origin:
            return False
        
        # Exact match
        if origin in FRONTEND_URLS:
            return True
        
        # Allow any Vercel deployment dynamically
        if 'vercel.app' in origin:
            return True
        
        # Allow localhost in development
        if os.getenv('FLASK_ENV') == 'development':
            if 'localhost' in origin or '127.0.0.1' in origin:
                return True
        
        return False

    @app.before_request
    def handle_preflight():
        """Handle CORS preflight (OPTIONS) requests"""
        if request.method == "OPTIONS":
            origin = request.headers.get('Origin', '')
            
            # Check origin before allowing
            if not is_origin_allowed(origin):
                logger.warning(f"[CORS] ❌ Rejected preflight from: {origin}")
                return '', 403
            
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
            response.headers['Access-Control-Max-Age'] = '86400'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Vary'] = 'Origin'
            
            logger.info(f"[CORS] ✅ Allowed preflight from: {origin}")
            return response, 204

    @app.after_request
    def add_cors_headers(response):
        """Add CORS headers to ALL responses"""
        origin = request.headers.get('Origin', '')
        
        # Only add CORS headers if origin is allowed
        if origin and is_origin_allowed(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
            response.headers['Vary'] = 'Origin'
            
            logger.debug(f"[CORS] ✅ Headers added for: {origin}")
        
        # Ensure Content-Type is application/json for API responses
        if request.path.startswith('/api/'):
            if not response.headers.get('Content-Type'):
                response.headers['Content-Type'] = 'application/json'
        
        return response

    return app
