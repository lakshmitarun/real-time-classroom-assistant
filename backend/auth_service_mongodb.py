import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

class AuthServiceMongoDB:
    def __init__(self, secret_key='your-secret-key-change-this'):
        self.secret_key = secret_key
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('MONGODB_DATABASE', 'classroomassisstant')
        self.collection_name = 'teachersignup'
        self.student_collection_name = 'student'
        
        # Initialize MongoDB connection
        self.client = None
        self.db = None
        self.collection = None
        self.student_collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            self.student_collection = self.db[self.student_collection_name]
            
            # Create index on email for faster lookups
            self.collection.create_index('email', unique=True)
            # Create index on user_id for student collection
            self.student_collection.create_index('user_id', unique=True)
            
            print(f"[OK] Connected to MongoDB - Database: {self.database_name}")
            print(f"[OK] Teacher Collection: {self.collection_name}")
            print(f"[OK] Student Collection: {self.student_collection_name}")
        except Exception as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}")
            raise
    
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
        
        try:
            # Check if email already exists
            existing = self.collection.find_one({'email': email})
            if existing:
                return {'success': False, 'message': 'Email already registered'}, 409
            
            # Generate teacher ID
            count = self.collection.count_documents({})
            teacher_id = f'T{count + 1000}'
            
            teacher = {
                'id': teacher_id,
                'email': email,
                'name': name,
                'password_hash': self.hash_password(password),
                'auth_method': 'email',
                'created_at': datetime.utcnow().isoformat(),
                'last_login': None,
                'google_id': None
            }
            
            result = self.collection.insert_one(teacher)
            teacher['_id'] = str(result.inserted_id)
            
            return ({
                'success': True,
                'message': 'Registration successful',
                'user': {
                    'id': teacher['id'],
                    'email': teacher['email'],
                    'name': teacher['name'],
                    'role': 'teacher'
                }
            }, 201)
        except Exception as e:
            print(f"[ERROR] Registration failed: {e}")
            return {'success': False, 'message': 'Registration failed'}, 500
    
    def login(self, email, password):
        """Login teacher with email and password"""
        email = email.lower().strip()
        
        try:
            teacher = self.collection.find_one({'email': email})
            
            if not teacher:
                return {'success': False, 'message': 'Invalid email or password'}, 401
            
            if not self.verify_password(password, teacher['password_hash']):
                return {'success': False, 'message': 'Invalid email or password'}, 401
            
            # Update last login
            self.collection.update_one(
                {'_id': teacher['_id']},
                {'$set': {'last_login': datetime.utcnow().isoformat()}}
            )
            
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
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            return {'success': False, 'message': 'Login failed'}, 500
    
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
        
        try:
            teacher = self.collection.find_one({'email': email})
            
            if not teacher:
                # Create new teacher account
                count = self.collection.count_documents({})
                teacher_id = f"T{count + 1000}"
                
                new_teacher = {
                    'id': teacher_id,
                    'email': email,
                    'name': name,
                    'google_id': google_id,
                    'auth_method': 'google',
                    'password_hash': '',
                    'created_at': datetime.utcnow().isoformat(),
                    'last_login': datetime.utcnow().isoformat()
                }
                
                result = self.collection.insert_one(new_teacher)
                teacher = new_teacher
                teacher['_id'] = str(result.inserted_id)
            else:
                # Update existing teacher - ensure name is set from Google if it's missing or empty
                update_data = {
                    'google_id': google_id,
                    'last_login': datetime.utcnow().isoformat()
                }
                
                # If teacher doesn't have a name or name is empty, update it from Google
                if not teacher.get('name') or teacher.get('name', '').strip() == '':
                    update_data['name'] = name
                
                self.collection.update_one(
                    {'_id': teacher['_id']},
                    {'$set': update_data}
                )
                
                # Refresh teacher object to get updated name
                teacher = self.collection.find_one({'_id': teacher['_id']})
            
            # Generate JWT token
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
        except Exception as e:
            print(f"[ERROR] Google login failed: {e}")
            return {'success': False, 'message': 'Google login failed'}, 500
    
    def get_teacher(self, user_id):
        """Get teacher by ID"""
        try:
            teacher = self.collection.find_one({'id': user_id})
            return teacher
        except Exception as e:
            print(f"[ERROR] Failed to get teacher: {e}")
            return None
    
    def student_login(self, user_id, password):
        """Login student with user ID and password"""
        user_id = user_id.strip()
        
        try:
            student = self.student_collection.find_one({'user_id': user_id})
            
            if not student:
                return {'success': False, 'message': 'Invalid user ID or password'}, 401
            
            # Verify password
            if not self.verify_password(password, student.get('password_hash', '')):
                return {'success': False, 'message': 'Invalid user ID or password'}, 401
            
            # Update last login
            self.student_collection.update_one(
                {'_id': student['_id']},
                {'$set': {'last_login': datetime.utcnow().isoformat()}}
            )
            
            # Generate JWT token
            token = self.generate_token(student['user_id'], student['user_id'])
            
            return ({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'userId': student['user_id'],
                    'name': student.get('name', ''),
                    'role': 'student',
                    'preferredLanguage': student.get('preferred_language', '')
                },
                'token': token
            }, 200)
        except Exception as e:
            print(f"[ERROR] Student login failed: {e}")
            return {'success': False, 'message': 'Login failed'}, 500
    
    def student_register(self, user_id, password, name, preferred_language=''):
        """Register a new student"""
        user_id = user_id.strip()
        
        try:
            # Check if user already exists
            existing = self.student_collection.find_one({'user_id': user_id})
            if existing:
                return {'success': False, 'message': 'User ID already registered'}, 409
            
            student = {
                'user_id': user_id,
                'name': name,
                'password_hash': self.hash_password(password),
                'preferred_language': preferred_language,
                'role': 'student',
                'created_at': datetime.utcnow().isoformat(),
                'last_login': None
            }
            
            result = self.student_collection.insert_one(student)
            student['_id'] = str(result.inserted_id)
            
            return ({
                'success': True,
                'message': 'Registration successful',
                'user': {
                    'userId': student['user_id'],
                    'name': student['name'],
                    'role': 'student'
                }
            }, 201)
        except Exception as e:
            print(f"[ERROR] Student registration failed: {e}")
            return {'success': False, 'message': 'Registration failed'}, 500
    
    def get_student(self, user_id):
        """Get student by ID"""
        try:
            student = self.student_collection.find_one({'user_id': user_id})
            return student
        except Exception as e:
            print(f"[ERROR] Failed to get student: {e}")
            return None
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("[OK] MongoDB connection closed")


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
        
        auth_service = AuthServiceMongoDB()
        result = auth_service.verify_token(token)
        
        if not result['valid']:
            return jsonify({'success': False, 'message': result['message']}), 401
        
        request.user = result['payload']
        return f(*args, **kwargs)
    
    return decorated_function
