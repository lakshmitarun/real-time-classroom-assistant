"""
JWT Token Handler
Handles JWT token generation and verification for authentication
"""
import jwt
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class JWTHandler:
    """
    JWT Token Handler for authentication
    Manages token generation and verification
    """
    
    def __init__(self):
        """Initialize JWT handler with environment variables"""
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        
        # Token expiration time in hours (default: 24 hours)
        try:
            self.expiration_hours = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
        except ValueError:
            self.expiration_hours = 24
            logger.warning("Invalid JWT_EXPIRATION_HOURS, using default 24 hours")
        
        if self.secret_key == 'your-secret-key-change-in-production':
            logger.warning("⚠️ JWT_SECRET_KEY is using default value. Change it in production!")
    
    def generate_token(self, user_data):
        """
        Generate JWT token for authenticated user
        
        Args:
            user_data (dict): User information to include in token
                Required keys:
                - _id or id: MongoDB ObjectId or user ID
                - email: User email
                - role: 'teacher' or 'student'
                - name (optional): User name
        
        Returns:
            str: JWT token
        
        Example:
            user_data = {
                '_id': ObjectId('...'),
                'email': 'user@example.com',
                'role': 'teacher',
                'name': 'John Doe'
            }
            token = jwt_handler.generate_token(user_data)
        """
        try:
            # Get user ID (support both _id from MongoDB and id)
            user_id = str(user_data.get('_id') or user_data.get('id'))
            
            # Create JWT payload
            payload = {
                'user_id': user_id,
                'email': user_data.get('email'),
                'role': user_data.get('role', 'student'),
                'name': user_data.get('name', ''),
                'iat': datetime.utcnow(),  # Issued at
                'exp': datetime.utcnow() + timedelta(hours=self.expiration_hours)  # Expiration
            }
            
            # Encode token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"✅ JWT token generated for user: {user_data.get('email')} ({user_id})")
            return token
        
        except Exception as e:
            logger.error(f"❌ Error generating JWT token: {str(e)}")
            raise
    
    def verify_token(self, token):
        """
        Verify and decode JWT token
        
        Args:
            token (str): JWT token to verify
        
        Returns:
            dict: Decoded token payload if valid, None if invalid/expired
        
        Example:
            payload = jwt_handler.verify_token(token)
            if payload:
                user_id = payload['user_id']
                email = payload['email']
                role = payload['role']
        """
        try:
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"✅ JWT token verified for user: {payload.get('email')}")
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning(f"❌ JWT token has expired")
            return None
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Invalid JWT token: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"❌ Error verifying JWT token: {str(e)}")
            return None
    
    def refresh_token(self, token):
        """
        Refresh an existing JWT token
        
        Args:
            token (str): Existing JWT token
        
        Returns:
            str: New JWT token if valid, None if invalid
        
        Example:
            new_token = jwt_handler.refresh_token(old_token)
            if new_token:
                # Use new token
                return {'token': new_token}
        """
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            # Create new payload with fresh expiration
            new_payload = {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'role': payload['role'],
                'name': payload.get('name', ''),
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=self.expiration_hours)
            }
            
            new_token = jwt.encode(new_payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✅ JWT token refreshed for user: {payload.get('email')}")
            return new_token
        
        except Exception as e:
            logger.error(f"❌ Error refreshing JWT token: {str(e)}")
            return None


# Create global instance
jwt_handler = JWTHandler()


def get_token_from_request(request):
    """
    Extract JWT token from request Authorization header
    
    Args:
        request: Flask request object
    
    Returns:
        str: Token string or None
    
    Example:
        from utils.jwt_handler import get_token_from_request
        
        @app.route('/api/protected')
        def protected_route():
            token = get_token_from_request(request)
            if not token:
                return {'error': 'Missing token'}, 401
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            logger.debug("No Authorization header found")
            return None
        
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            logger.warning("Invalid Authorization header format")
            return None
        
        token = parts[1]
        logger.debug("Token extracted from Authorization header")
        return token
    
    except Exception as e:
        logger.error(f"Error extracting token from request: {str(e)}")
        return None
