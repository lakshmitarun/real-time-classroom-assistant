import json
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

class AuthService:
    def __init__(self, secret_key='your-secret-key-change-this'):
        self.secret_key = secret_key
        self.teachers_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'teachers.json')
        self.teachers_db = self._load_teachers()
    
    def _load_teachers(self):
        """Load teachers from JSON file"""
        if os.path.exists(self.teachers_file):
            try:
                with open(self.teachers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading teachers: {e}")
        return {}
    
    def _save_teachers(self):
        """Save teachers to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.teachers_file), exist_ok=True)
            with open(self.teachers_file, 'w', encoding='utf-8') as f:
                json.dump(self.teachers_db, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving teachers: {e}")
            return False
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def register(self, email, password, name):
        """Register a new teacher"""
        email = email.lower().strip()
        
        # Check if teacher already exists
        if email in self.teachers_db:
            return {'error': 'Email already registered'}, 409
        
        if not password or len(password) < 6:
            return {'error': 'Password must be at least 6 characters'}, 400
        
        # Create teacher record
        teacher_id = f"T{len(self.teachers_db) + 1000}"
        hashed_password = self.hash_password(password)
        
        self.teachers_db[email] = {
            'id': teacher_id,
            'email': email,
            'name': name,
            'password_hash': hashed_password,
            'auth_method': 'email',
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None
        }
        
        if not self._save_teachers():
            return {'error': 'Failed to save teacher'}, 500
        
        return {'success': True, 'teacher_id': teacher_id, 'message': 'Registration successful'}, 201
    
    def login(self, email, password):
        """Login with email and password"""
        email = email.lower().strip()
        
        if email not in self.teachers_db:
            return {'error': 'Invalid email or password'}, 401
        
        teacher = self.teachers_db[email]
        
        if teacher['auth_method'] == 'google':
            return {'error': 'This account uses Google login. Use "Sign in with Google" instead.'}, 401
        
        if not self.verify_password(password, teacher['password_hash']):
            return {'error': 'Invalid email or password'}, 401
        
        # Update last login
        teacher['last_login'] = datetime.utcnow().isoformat()
        self._save_teachers()
        
        # Generate JWT token
        token = self.generate_token(email)
        
        return {
            'success': True,
            'token': token,
            'role': 'teacher',
            'teacher': {
                'id': teacher['id'],
                'email': teacher['email'],
                'name': teacher['name'],
                'role': 'teacher'
            }
        }, 200
    
    def google_login(self, email, name, google_id):
        """Login or register with Google"""
        email = email.lower().strip()
        
        if email not in self.teachers_db:
            # Create new teacher account
            teacher_id = f"T{len(self.teachers_db) + 1000}"
            self.teachers_db[email] = {
                'id': teacher_id,
                'email': email,
                'name': name,
                'google_id': google_id,
                'auth_method': 'google',
                'created_at': datetime.utcnow().isoformat(),
                'last_login': datetime.utcnow().isoformat()
            }
        else:
            # Update existing teacher
            teacher = self.teachers_db[email]
            teacher['google_id'] = google_id
            teacher['last_login'] = datetime.utcnow().isoformat()
        
        self._save_teachers()
        
        # Generate JWT token
        token = self.generate_token(email)
        teacher = self.teachers_db[email]
        
        return {
            'success': True,
            'token': token,
            'role': 'teacher',
            'teacher': {
                'id': teacher['id'],
                'email': teacher['email'],
                'name': teacher['name'],
                'role': 'teacher'
            }
        }, 200
    
    def generate_token(self, email, expires_in=86400):
        """Generate JWT token (valid for 24 hours by default)"""
        payload = {
            'email': email,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token and return email"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload.get('email')
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_teacher(self, email):
        """Get teacher info"""
        email = email.lower().strip()
        if email in self.teachers_db:
            teacher = self.teachers_db[email].copy()
            teacher.pop('password_hash', None)  # Don't return password hash
            return teacher
        return None


def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # You'll need to pass auth_service instance to the decorated function
        # This is handled in app.py
        return f(*args, **kwargs)
    
    return decorated
