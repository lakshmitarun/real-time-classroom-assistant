"""
Authentication Routes
Handles Google OAuth, JWT token generation, and user login
"""
from flask import Blueprint, request, jsonify
import logging
import json
import base64
from datetime import datetime
from utils.jwt_handler import jwt_handler

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)


@auth_bp.route('/google/callback', methods=['POST', 'OPTIONS'])
def google_callback():
    """
    Google OAuth Callback Endpoint
    
    Expects JSON:
    {
        "credential": "<Google ID Token>" OR "token": "<Google ID Token>",
        "role": "teacher" (optional, defaults to "teacher")
    }
    
    Returns:
    {
        "success": true,
        "message": "Login successful",
        "token": "<JWT Token>",
        "user": {
            "id": "...",
            "email": "...",
            "name": "...",
            "role": "teacher"
        }
    }
    """
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("❌ Empty request body for Google callback")
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
        
        # Support both 'credential' (from frontend) and 'token' (from API)
        google_token = data.get('credential') or data.get('token', '')
        google_token = google_token.strip()
        role = data.get('role', 'teacher').lower()
        
        if not google_token:
            logger.warning("❌ Missing 'token' in Google callback request")
            return jsonify({
                'success': False,
                'error': 'Missing token'
            }), 400
        
        logger.info(f"🔐 Processing Google callback with role: {role}")
        
        # Decode JWT to extract user information
        # Note: In production, you should verify the signature with Google's public keys
        try:
            parts = google_token.split('.')
            if len(parts) != 3:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token format'
                }), 400
            
            # Decode the payload (2nd part)
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            
            email = decoded.get('email', '').lower().strip()
            name = decoded.get('name', 'User')
            google_id = decoded.get('sub', '')
            
            if not email:
                logger.warning("❌ Could not extract email from Google token")
                return jsonify({
                    'success': False,
                    'error': 'Could not extract email from token'
                }), 400
            
            logger.info(f"✅ Decoded Google token - Email: {email}, Name: {name}")
            
            # Import auth_service from parent app context
            from auth_service_mongodb import AuthServiceMongoDB
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            try:
                # Initialize auth service if not already done
                auth_service = AuthServiceMongoDB(
                    secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key')
                )
                
                # Use google_login function from auth_service
                result, status_code = auth_service.google_login(email, name, google_id)
                
                if result.get('success'):
                    # Get teacher data from result (auth_service returns 'teacher' not 'user')
                    teacher_data = result.get('teacher', {})
                    
                    # Generate JWT token
                    try:
                        jwt_token = jwt_handler.generate_token({
                            '_id': teacher_data.get('id') or teacher_data.get('_id'),
                            'email': email,
                            'name': name,
                            'role': role
                        })
                        
                        logger.info(f"✅ JWT token generated for Google login: {email}")
                        
                        # Return response with JWT token
                        # Include both 'user' and 'teacher' fields for frontend compatibility
                        user_obj = {
                            'id': teacher_data.get('id') or teacher_data.get('_id'),
                            'email': email,
                            'name': name,
                            'role': role
                        }
                        return jsonify({
                            'success': True,
                            'message': 'Google login successful',
                            'token': jwt_token,
                            'role': role,
                            'user': user_obj,
                            'teacher': user_obj
                        }), 200
                    
                    except Exception as e:
                        logger.error(f"❌ JWT generation error: {str(e)}")
                        return jsonify({
                            'success': False,
                            'error': 'Failed to generate token'
                        }), 500
                else:
                    logger.warning(f"❌ Google login failed: {result.get('message')}")
                    return jsonify(result), status_code
            
            except Exception as e:
                logger.error(f"❌ Auth service error: {str(e)}")
                # Fallback: Return success with temporary token for demo
                logger.warning(f"⚠️ Using fallback mode for Google login")
                demo_token = f"demo_{google_id}_{int(datetime.now().timestamp())}"
                
                fallback_user = {
                    'id': f'google-{google_id[:8]}',
                    'email': email,
                    'name': name,
                    'role': role
                }
                return jsonify({
                    'success': True,
                    'message': 'Login successful (Fallback Mode)',
                    'token': demo_token,
                    'role': role,
                    'user': fallback_user,
                    'teacher': fallback_user
                }), 200
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to decode Google token: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid token format'
            }), 400
    
    except Exception as e:
        logger.error(f"❌ Google callback error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Email/Password Login Endpoint
    
    Expects JSON:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Login successful",
        "token": "<JWT Token>",
        "user": { ... }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        logger.info(f"🔐 Login attempt for: {email}")
        
        from auth_service_mongodb import AuthServiceMongoDB
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        try:
            auth_service = AuthServiceMongoDB(
                secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key')
            )
            
            result, status_code = auth_service.login(email, password)
            
            if result.get('success'):
                logger.info(f"✅ Login successful for: {email}")
                
                # Generate JWT token
                try:
                    user_data = result.get('user', {})
                    jwt_token = jwt_handler.generate_token({
                        '_id': user_data.get('id') or user_data.get('_id'),
                        'email': email,
                        'name': user_data.get('name', ''),
                        'role': user_data.get('role', 'teacher')
                    })
                    
                    logger.info(f"✅ JWT token generated for login: {email}")
                    
                    # Add token to response and ensure both 'user' and 'teacher' fields
                    result['token'] = jwt_token
                    result['role'] = user_data.get('role', 'teacher')
                    result['teacher'] = user_data  # Add teacher field for frontend
                    return jsonify(result), status_code
                
                except Exception as e:
                    logger.error(f"❌ JWT generation error: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to generate token'
                    }), 500
            else:
                logger.warning(f"❌ Login failed for: {email}")
                return jsonify(result), status_code
        
        except Exception as e:
            logger.error(f"❌ Auth service error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User Registration Endpoint
    
    Expects JSON:
    {
        "email": "user@example.com",
        "password": "password123",
        "name": "User Name",
        "role": "teacher" (optional)
    }
    
    Returns:
    {
        "success": true,
        "message": "Registration successful",
        "user": { ... }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({
                'success': False,
                'error': 'Email, password, and name are required'
            }), 400
        
        logger.info(f"📝 Registration attempt for: {email}")
        
        from auth_service_mongodb import AuthServiceMongoDB
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        try:
            auth_service = AuthServiceMongoDB(
                secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key')
            )
            
            result, status_code = auth_service.register(email, password, name)
            
            if result.get('success'):
                logger.info(f"✅ Registration successful for: {email}")
            else:
                logger.warning(f"❌ Registration failed for: {email} - {result.get('message')}")
            
            return jsonify(result), status_code
        
        except Exception as e:
            logger.error(f"❌ Auth service error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Registration failed'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout Endpoint
    Clears user session (tokens are handled client-side)
    
    Returns:
    {
        "success": true,
        "message": "Logged out successfully"
    }
    """
    try:
        logger.info("👋 User logged out")
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500
