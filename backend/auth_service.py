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
        # Use local JSON file for teacher storage
        self.teachers_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'teachers.json')
        self.teachers_db = self._load_teachers()
    
    def _load_teachers(self):
        """Load teachers from local JSON file"""
        try:
            if os.path.exists(self.teachers_file):
                with open(self.teachers_file, 'r', encoding='utf-8') as f:
                    teachers = json.load(f)
                    print(f"[OK] Teachers loaded from local file: {len(teachers)} records")
                    return teachers
            else:
                print("[WARNING] Teachers file not found, starting with empty database")
                return {}
        except Exception as e:
            print(f"[ERROR] Error loading teachers: {e}")
            return {}
    
    def _save_teachers(self):
        """Save teachers to local JSON file"""
        try:
            os.makedirs(os.path.dirname(self.teachers_file), exist_ok=True)
            with open(self.teachers_file, 'w', encoding='utf-8') as f:
                json.dump(self.teachers_db, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] Error saving teachers: {e}")
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
        
        if email in self.teachers_db:
            return {'success': False, 'message': 'Email already registered'}, 409
        
        teacher = {
            'id': f'T{len(self.teachers_db) + 1000}',
            'email': email,
            'name': name,
            'password_hash': self.hash_password(password),
            'auth_method': 'email',
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None,
            'google_id': None
        }
        
        self.teachers_db[email] = teacher
        self._save_teachers()
        return ({'success': True, 'message': 'Registration successful', 'user': teacher}, 201)
    
    def login(self, email, password):
        """Login teacher with email and password"""
        email = email.lower().strip()
        
        if email not in self.teachers_db:
            return {'success': False, 'message': 'Invalid email or password'}, 401
        
        teacher = self.teachers_db[email]
        if not self.verify_password(password, teacher['password_hash']):
            return {'success': False, 'message': 'Invalid email or password'}, 401
        
        # Update last login
        teacher['last_login'] = datetime.utcnow().isoformat()
        self._save_teachers()
        
        # Generate JWT token
        token = self.generate_token(teacher['id'], teacher['email'])
        return ({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': teacher['id'],
                'email': teacher['email'],
                'name': teacher['name'],
                'role': 'teacher'
            },
            'token': token,
            'teacher': {
                'id': teacher['id'],
                'email': teacher['email'],
                'name': teacher['name'],
                'role': 'teacher'
            }
        }, 200)
    
    def generate_token(self, user_id, email):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'message': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'message': 'Invalid token'}
    
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
                'password_hash': '',  # No password for Google auth
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
        teacher = self.teachers_db[email]
        token = self.generate_token(teacher['id'], teacher['email'])
        
        return ({
            'success': True,
            'token': token,
            'role': 'teacher',
            'teacher': {
                'id': teacher['id'],
                'email': teacher['email'],
                'name': teacher['name'],
                'auth_method': 'google'
            }
        }, 200)
    
    def get_teacher(self, user_id):
        """Get teacher by ID"""
        for email, teacher in self.teachers_db.items():
            if teacher.get('id') == user_id:
                return teacher
        return None

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token required'}), 401
        
        auth_service = AuthService()
        result = auth_service.verify_token(token)
        
        if not result['valid']:
            return jsonify({'success': False, 'message': result['message']}), 401
        
        request.user = result['payload']
        return f(*args, **kwargs)
    
    return decorated_function
