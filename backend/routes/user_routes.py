"""
User Routes
Handles user profile, preferences, and related operations
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from utils.jwt_handler import jwt_handler, get_token_from_request

# Create Blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/user')
logger = logging.getLogger(__name__)


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    Get Current User Profile (JWT Protected)
    
    Requires Authorization header:
    Authorization: Bearer <jwt_token>
    
    Returns:
    {
        "success": true,
        "user": {
            "id": "...",
            "email": "...",
            "name": "...",
            "role": "teacher",
            "created_at": "..."
        }
    }
    """
    try:
        # Extract token from Authorization header
        token = get_token_from_request(request)
        
        if not token:
            logger.warning("❌ Missing Authorization token for profile request")
            return jsonify({
                'success': False,
                'error': 'Missing or invalid Authorization header'
            }), 401
        
        # Verify JWT token
        payload = jwt_handler.verify_token(token)
        
        if not payload:
            logger.warning("❌ Invalid or expired JWT token")
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        user_email = payload.get('email')
        logger.info(f"📋 User profile requested for: {user_email}")
        
        # Fetch user from MongoDB
        try:
            from auth_service_mongodb import AuthServiceMongoDB
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            auth_service = AuthServiceMongoDB(
                secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key')
            )
            
            # Determine if user is teacher or student based on role
            role = payload.get('role', 'teacher')
            
            if role == 'teacher':
                # Fetch from teachersignup collection
                user = auth_service.collection.find_one({'email': user_email})
            else:
                # Fetch from student collection
                user = auth_service.student_collection.find_one({'email': user_email})
            
            if not user:
                logger.warning(f"❌ User not found in database: {user_email}")
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Format user data
            user_profile = {
                'id': str(user.get('_id', user.get('id', ''))),
                'email': user.get('email', ''),
                'name': user.get('name', ''),
                'role': user.get('role', role),
                'created_at': user.get('created_at', datetime.utcnow().isoformat()),
                'last_login': user.get('last_login', datetime.utcnow().isoformat())
            }
            
            logger.info(f"✅ Profile retrieved for user: {user_email}")
            
            return jsonify({
                'success': True,
                'user': user_profile
            }), 200
        
        except Exception as e:
            logger.error(f"❌ Error fetching user from database: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve user profile'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ Error getting profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """
    Update User Profile
    
    Expects JSON:
    {
        "name": "Updated Name",
        "email": "newemail@example.com",
        "role": "student"
    }
    
    Returns:
    {
        "success": true,
        "message": "Profile updated successfully",
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
        
        logger.info("✏️ Updating user profile")
        
        # In production, verify JWT token and get user ID
        # Extract fields to update
        updates = {}
        if 'name' in data:
            updates['name'] = data['name'].strip()
        if 'email' in data:
            updates['email'] = data['email'].strip().lower()
        if 'role' in data:
            updates['role'] = data['role'].lower()
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'No fields to update'
            }), 400
        
        # In production: Update in database
        # For now: Return success
        
        updated_profile = {
            "id": "user_123",
            "email": updates.get('email', 'user@example.com'),
            "name": updates.get('name', 'John Doe'),
            "role": updates.get('role', 'teacher'),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info("✅ Profile updated successfully")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': updated_profile
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile'
        }), 500


@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get User By ID
    
    Returns:
    {
        "success": true,
        "user": { ... }
    }
    """
    try:
        logger.info(f"📋 User data requested for: {user_id}")
        
        # In production: Fetch from database
        # For now: Return example data
        
        user = {
            "id": user_id,
            "email": "user@example.com",
            "name": "John Doe",
            "role": "teacher",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error getting user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user'
        }), 500


@user_bp.route('/all', methods=['GET'])
def get_all_users():
    """
    Get All Users (Admin Only)
    
    Returns:
    {
        "success": true,
        "users": [ ... ],
        "total": 10
    }
    """
    try:
        logger.info("📋 All users requested")
        
        # In production: Verify JWT and check role is 'admin'
        # then fetch from database
        
        users = [
            {
                "id": "user_1",
                "email": "teacher1@example.com",
                "name": "Teacher One",
                "role": "teacher",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "user_2",
                "email": "student1@example.com",
                "name": "Student One",
                "role": "student",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'users': users,
            'total': len(users)
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error getting all users: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get users'
        }), 500


@user_bp.route('/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete User (Admin Only)
    
    Returns:
    {
        "success": true,
        "message": "User deleted successfully"
    }
    """
    try:
        logger.info(f"🗑️ Delete user requested for: {user_id}")
        
        # In production: Verify JWT and check role is 'admin'
        # then delete from database
        
        logger.info(f"✅ User deleted: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error deleting user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete user'
        }), 500
