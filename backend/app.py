
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
import pickle
import logging
import traceback
from threading import Lock
from dotenv import load_dotenv
from services.translation_service import TranslationService
from services.speech_service import SpeechService
from auth_service_mongodb import AuthServiceMongoDB, token_required
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from datetime import datetime
import random
import string

load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for production and development
# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = [
    # Development
    "http://localhost:3001",
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5173",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # Production - Main Vercel deployment
    "https://real-time-classroom-assistant.vercel.app",
    # Production - Vercel preview/alternative deployments
    "https://real-time-classroom-assistant-2ze2pt6u7.vercel.app",
    "https://real-time-classroom-assistant-n4yjfaano.vercel.app",
    "https://classroom-assistant-frontend.vercel.app",
    "https://real-time-classroom-assistant-dc1mdzsl5.vercel.app",
    "https://real-time-classroom-assistant-ye11.vercel.app",
    "https://real-time-classroom-git-d6393a-palivela-lakshmi-taruns-projects.vercel.app",
]

# Add custom origins from environment variable if set
if os.getenv('CORS_ORIGINS'):
    ALLOWED_ORIGINS.extend(os.getenv('CORS_ORIGINS', '').split(','))

def check_origin(origin):
    """Check if origin is allowed"""
    if not origin:
        return True
    # Allow all known origins
    if origin in ALLOWED_ORIGINS:
        logger.info(f"[CORS] ✅ Allowed origin: {origin}")
        return True
    # Allow all Vercel deployments dynamically
    if 'vercel.app' in origin:
        logger.info(f"[CORS] ✅ Allowed Vercel domain: {origin}")
        return True
    # Allow all dev tunnel origins dynamically
    if 'devtunnels.ms' in origin:
        logger.info(f"[CORS] ✅ Allowed dev tunnel: {origin}")
        return True
    # Allow localhost variants
    if 'localhost' in origin or '127.0.0.1' in origin:
        logger.info(f"[CORS] ✅ Allowed localhost: {origin}")
        return True
    logger.warning(f"[CORS] ❌ Rejected origin: {origin}")
    return False

# Configure CORS for all routes with proper production settings
CORS(app, 
    resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS,  # Use specific origins instead of "*"
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,  # Allow credentials (cookies, auth headers)
            "max_age": 3600,
        }
    },
    intercept_exceptions=False
)

# Handle preflight requests explicitly
@app.before_request
def handle_preflight():
    """Handle CORS preflight requests"""
    origin = request.headers.get("Origin", "unknown")
    logger.info(f"[REQUEST] {request.method} {request.path} from {origin}")
    
    if request.method == "OPTIONS":
        logger.info(f"[PREFLIGHT] Handling OPTIONS request from {origin}")
        response = jsonify({'status': 'ok'})
        
        # Always return proper CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin if origin and origin != "unknown" else "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        response.headers["Access-Control-Max-Age"] = "3600"
        response.headers["Content-Type"] = "application/json"
        
        logger.info(f"[PREFLIGHT] Response headers set for {origin}")
        return response, 200

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to ALL responses"""
    origin = request.headers.get("Origin")
    
    # Always set CORS headers
    response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    response.headers["Access-Control-Expose-Headers"] = "Content-Type"
    response.headers["Vary"] = "Origin"
    
    # Ensure Content-Type is set
    if not response.headers.get("Content-Type"):
        response.headers["Content-Type"] = "application/json"
    
    return response

# Global error handler for 404
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.method} {request.path}")
    response = jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path,
        'method': request.method
    })
    response.status_code = 404
    response.headers['Content-Type'] = 'application/json'
    return response

# Global error handler for 500
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {str(error)}\n{traceback.format_exc()}")
    response = jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error) if app.debug else 'An error occurred'
    })
    response.status_code = 500
    response.headers['Content-Type'] = 'application/json'
    return response

# Ensure all responses have correct Content-Type
@app.after_request
def set_json_response_headers(response):
    """Ensure all API responses have proper JSON headers"""
    if request.path.startswith('/api/'):
        response.headers['Content-Type'] = 'application/json'
    return response

# Initialize services
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
translation_service = None
speech_service = None
auth_service = None

try:
    translation_service = TranslationService()
    speech_service = SpeechService()
    auth_service = AuthServiceMongoDB(secret_key=os.getenv('JWT_SECRET_KEY', 'classroom-assistant-secret-key'))
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    if translation_service is None:
        translation_service = None
    if speech_service is None:
        speech_service = None
    if auth_service is None:
        auth_service = None

# Log OAuth configuration
if GOOGLE_CLIENT_ID:
    logger.info(f"[OK] Google OAuth configured: {GOOGLE_CLIENT_ID[:20]}...")
else:
    logger.warning("[WARNING] GOOGLE_CLIENT_ID not set!")


# Track active student sessions
active_sessions = {}

# Track active teacher sessions with join codes
active_teacher_sessions = {}

# Persistent login history
login_history_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'login_history.pkl')
login_history_lock = Lock()
if os.path.exists(login_history_file):
    with open(login_history_file, 'rb') as f:
        login_history = pickle.load(f)
else:
    login_history = set()

# Root route - shows the API is running
@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Classroom Assistant API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'student_login': '/api/student/login',
            'teacher_login': '/api/auth/login'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check"""
    try:
        logger.info("Health check requested")
        return jsonify({
            'status': 'healthy',
            'message': 'Classroom Assistant API is running',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'unhealthy', 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Detailed system status"""
    try:
        logger.info("Status check requested")
        
        # Check translation database
        db = getattr(translation_service, 'translation_db', None)
        db_healthy = db and 'english' in db
        total_translations = len(db.get('english', {})) if db_healthy else 0
        
        # Check teacher sessions
        active_classes = len(active_teacher_sessions)
        
        status_data = {
            'status': 'healthy' if db_healthy else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'translation_db': {
                    'healthy': db_healthy,
                    'entries': total_translations
                },
                'auth_service': {
                    'healthy': bool(auth_service),
                    'configured': bool(auth_service.collection) if auth_service else False
                },
                'google_oauth': {
                    'configured': bool(GOOGLE_CLIENT_ID)
                }
            },
            'active_sessions': {
                'student_sessions': len(active_sessions),
                'active_classes': active_classes
            }
        }
        
        return jsonify(status_data), 200 if db_healthy else 503
    
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'status': 'unhealthy', 'message': str(e)}), 500

@app.route('/api/ready', methods=['GET'])
def readiness():
    """Readiness probe for deployment orchestration"""
    try:
        # Check if system is ready to accept traffic
        db = getattr(translation_service, 'translation_db', None)
        if not db or 'english' not in db:
            logger.error("Readiness check failed: Translation DB not loaded")
            return jsonify({'ready': False, 'reason': 'Translation database not loaded'}), 503
        
        if len(db.get('english', {})) < 2400:
            logger.warning(f"Readiness check warning: Only {len(db['english'])} translations loaded (expected 2492+)")
        
        logger.info(f"Readiness check passed: {len(db['english'])} translations loaded")
        return jsonify({'ready': True, 'translations_loaded': len(db['english'])}), 200
    
    except Exception as e:
        logger.error(f"Readiness check error: {str(e)}")
        return jsonify({'ready': False, 'reason': str(e)}), 503

# ============ AUTHENTICATION ENDPOINTS ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new teacher account"""
    try:
        data = request.json
        if not data:
            logger.warning("Register: No JSON data provided")
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            logger.warning(f"Register: Missing required fields - email={bool(email)}, password={bool(password)}, name={bool(name)}")
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[-1]:
            logger.warning(f"Register: Invalid email format - {email}")
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        logger.info(f"Register attempt: {email}")
        result, status_code = auth_service.register(email, password, name)
        
        if status_code == 200 or status_code == 201:
            logger.info(f"Register successful: {email}")
        else:
            logger.warning(f"Register failed: {email} - {result}")
        
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Register error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            logger.warning("Login: No JSON data received")
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            logger.warning(f"Login: Missing credentials - email={bool(email)}, password={bool(password)}")
            return jsonify({'error': 'Email and password are required'}), 400
        
        logger.info(f"Login attempt: {email}")
        result, status_code = auth_service.login(email, password)
        if status_code == 200:
            logger.info(f"✅ Login successful: {email}")
        else:
            logger.warning(f"Login failed: {email} - Status {status_code}")
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/google/callback', methods=['POST'])
def google_callback():
    """Handle Google OAuth callback - frontend sends Google token"""
    try:
        data = request.json or {}
        logger.info(f"Google callback received from: {request.headers.get('Origin')}")

        # Accept either a client-verified ID token (credential) or legacy { email, name, id }
        credential = data.get('credential') or data.get('id_token')
        if credential:
            if not GOOGLE_CLIENT_ID:
                logger.error("Google callback: GOOGLE_CLIENT_ID not configured")
                return jsonify({'error': 'Server misconfigured: GOOGLE_CLIENT_ID not set'}), 500
            try:
                logger.info("Verifying Google ID token...")
                idinfo = id_token.verify_oauth2_token(credential, grequests.Request(), GOOGLE_CLIENT_ID)
                logger.info(f"Token verified for: {idinfo.get('email')}")
            except ValueError as e:
                logger.warning(f"Invalid ID token: {str(e)}")
                return jsonify({'error': f'Invalid ID token: {str(e)}'}), 400

            email = idinfo.get('email', '').strip()
            name = idinfo.get('name', '') or idinfo.get('given_name', '')
            google_id = idinfo.get('sub', '')

            if not email or not google_id:
                logger.warning(f"Token missing fields: email={bool(email)}, sub={bool(google_id)}")
                return jsonify({'error': 'ID token missing required fields'}), 400

            try:
                logger.info(f"Processing Google login: {email}")
                result = auth_service.google_login(email, name, google_id)
                if isinstance(result, tuple):
                    result, status_code = result
                else:
                    status_code = 200
                if status_code == 200:
                    logger.info(f"Google login successful: {email}")
                else:
                    logger.warning(f"Google login failed: {email} - Status {status_code}")
                return jsonify(result), status_code
            except Exception as e:
                logger.error(f"Google login error: {str(e)}\n{traceback.format_exc()}")
                return jsonify({'error': f'Login failed: {str(e)}'}), 500

        # Fallback: legacy payload
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        google_id = data.get('id', '').strip()

        if not email or not google_id:
            logger.warning("Legacy Google payload missing fields")
            return jsonify({'error': 'Email and Google ID are required'}), 400

        result, status_code = auth_service.google_login(email, name, google_id)
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Google callback error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    """Verify if JWT token is valid"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            logger.warning("Verify token: No token provided")
            return jsonify({'error': 'No token provided'}), 401
        
        email = auth_service.verify_token(token)
        if not email:
            logger.warning("Verify token: Invalid or expired token")
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        teacher = auth_service.get_teacher(email)
        logger.info(f"Token verified for: {email}")
        return jsonify({
            'valid': True,
            'teacher': teacher
        }), 200
    
    except Exception as e:
        logger.error(f"Verify token error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/teacher/profile', methods=['GET'])
def get_teacher_profile():
    """Get current teacher profile (requires auth)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            logger.warning("Get profile: No token provided")
            return jsonify({'error': 'No token provided'}), 401
        
        email = auth_service.verify_token(token)
        if not email:
            logger.warning("Get profile: Invalid token")
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        teacher = auth_service.get_teacher(email)
        if not teacher:
            logger.warning(f"Get profile: Teacher not found - {email}")
            return jsonify({'error': 'Teacher not found'}), 404
        
        logger.info(f"Profile retrieved for: {email}")
        return jsonify(teacher), 200
    
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text to target languages"""
    try:
        data = request.json
        if not data:
            logger.warning("Translate: No JSON data provided")
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'english').lower()
        target_lang = data.get('target_lang', 'bodo').lower()
        
        if not text:
            logger.warning("Translate: No text provided")
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:
            logger.warning(f"Translate: Text too long ({len(text)} chars)")
            return jsonify({'error': 'Text too long (max 1000 chars)'}), 400
        
        logger.info(f"Translate: '{text[:50]}...' {source_lang}→{target_lang}")
        translation = translation_service.translate(text, source_lang, target_lang)
        
        return jsonify({
            'source_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'translation': translation,
            'confidence': 0.95
        }), 200
    
    except Exception as e:
        logger.error(f"Translate error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/api/translate/batch', methods=['POST'])
def translate_batch():
    """Translate text to multiple languages at once"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'english').lower()
        
        if not text:
            logger.warning("Batch translate: No text provided")
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:
            logger.warning(f"Batch translate: Text too long ({len(text)} chars)")
            return jsonify({'error': 'Text too long (max 1000 chars)'}), 400
        
        logger.info(f"Batch translate: '{text[:30]}...'")
        translations = {
            'bodo': translation_service.translate(text, source_lang, 'bodo'),
            'mizo': translation_service.translate(text, source_lang, 'mizo'),
            'english': translation_service.translate(text, source_lang, 'english')
        }
        
        return jsonify({
            'source_text': text,
            'source_lang': source_lang,
            'translations': translations
        }), 200
    
    except Exception as e:
        logger.error(f"Batch translate error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Batch translation failed: {str(e)}'}), 500

@app.route('/api/speech/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        text = data.get('text', '').strip()
        language = data.get('language', 'english').lower()
        
        if not text:
            logger.warning("TTS: No text provided")
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 500:
            logger.warning(f"TTS: Text too long ({len(text)} chars)")
            return jsonify({'error': 'Text too long (max 500 chars)'}), 400
        
        if language not in ['english', 'bodo', 'mizo', 'hindi']:
            logger.warning(f"TTS: Unsupported language - {language}")
            return jsonify({'error': f'Unsupported language: {language}'}), 400
        
        logger.info(f"TTS: '{text[:30]}...' in {language}")
        audio_url = speech_service.text_to_speech(text, language)
        
        return jsonify({
            'text': text,
            'language': language,
            'audio_url': audio_url
        }), 200
    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'TTS conversion failed: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout and clear session"""
    try:
        data = request.json or {}
        user_id = data.get('userId', '').strip()
        
        if not user_id:
            logger.warning("Logout: No user ID provided")
            return jsonify({
                'success': False,
                'message': 'User ID required'
            }), 400
        
        if user_id in active_sessions:
            del active_sessions[user_id]
            logger.info(f"Logout successful: {user_id}")
            return jsonify({
                'success': True,
                'message': 'Logged out successfully'
            }), 200
        
        logger.warning(f"Logout: Session not found - {user_id}")
        return jsonify({
            'success': False,
            'message': 'Session not found'
        }), 404
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }), 500

@app.route('/api/active-students', methods=['GET'])
def get_active_students():
    """Get list of active student sessions"""
    try:
        logger.info(f"Active students check: {len(active_sessions)} students")
        return jsonify({
            'count': len(active_sessions),
            'students': list(active_sessions.values())
        }), 200
    except Exception as e:
        logger.error(f"Get active students error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/classrooms', methods=['GET'])
def get_classrooms():
    """Get list of active classrooms"""
    try:
        logger.info(f"🔍 Classrooms endpoint called - {len(active_teacher_sessions)} active sessions")
        classrooms = []
        for join_code, session in active_teacher_sessions.items():
            classroom = {
                'joinCode': join_code,
                'teacher': session.get('teacherName', 'Unknown'),
                'subject': session.get('subject', 'General'),
                'students': len(session.get('students', [])),
                'startTime': session.get('createdAt', ''),
                'status': 'active' if session.get('isActive', True) else 'ended'
            }
            classrooms.append(classroom)
            logger.info(f"  📍 Classroom: {classroom}")
        
        logger.info(f"✅ Returning {len(classrooms)} active classrooms")
        return jsonify({
            'count': len(classrooms),
            'classrooms': classrooms
        }), 200
    except Exception as e:
        logger.error(f"Get classrooms error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        with login_history_lock:
            total_unique_logins = len(login_history)
        
        # Get total teachers from MongoDB
        total_teachers = 0
        try:
            if auth_service and auth_service.collection:
                total_teachers = auth_service.collection.count_documents({})
        except Exception as e:
            logger.warning(f"Could not count teachers: {str(e)}")
        
        # Get total students from CSV
        total_students = 0
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'classroom_dataset_complete.csv')
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    total_students = sum(1 for _ in reader)
        except Exception as e:
            logger.warning(f"Could not count students: {str(e)}")
        
        logger.info(f"Stats requested: {len(active_sessions)} active sessions, {total_teachers} teachers, {total_students} students")
        return jsonify({
            'active_classrooms': len(active_teacher_sessions),
            'total_teachers': total_teachers,
            'total_students': total_students,
            'logged_in_students': len(active_sessions),
            'total_unique_logins': total_unique_logins,
            'avg_accuracy': 0,
            'avg_latency': 1.8,
            'total_translations': 0
        }), 200
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translation-stats', methods=['GET'])
def get_translation_stats():
    """Return translation statistics computed from loaded dataset"""
    try:
        logger.info("Translation stats requested")
        
        db = getattr(translation_service, 'translation_db', None)
        if not db or 'english' not in db:
            logger.error("Translation database not loaded")
            return jsonify({'success': False, 'message': 'Translation database not loaded'}), 503

        total = len(db['english'])
        bodo_count = 0
        mizo_count = 0

        for k, entry in db['english'].items():
            if isinstance(entry, dict):
                bodo = entry.get('bodo', '')
                mizo = entry.get('mizo', '')
                if bodo and str(bodo).strip():
                    bodo_count += 1
                if mizo and str(mizo).strip():
                    mizo_count += 1

        bodo_pct = round((bodo_count / total * 100), 1) if total > 0 else 0
        mizo_pct = round((mizo_count / total * 100), 1) if total > 0 else 0

        stats = [
            {'language': 'English → Bodo', 'count': bodo_count, 'accuracy': bodo_pct},
            {'language': 'English → Mizo', 'count': mizo_count, 'accuracy': mizo_pct}
        ]

        logger.info(f"Translation stats: {bodo_count} Bodo, {mizo_count} Mizo translations")
        return jsonify({'success': True, 'stats': stats, 'total_entries': total}), 200
    
    except Exception as e:
        logger.error(f"Get translation stats error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/student/login', methods=['POST'])
def student_login():
    """Student login with user ID and password (MongoDB or Demo Mode)"""
    try:
        data = request.json
        if not data:
            logger.warning("Student login: No JSON data provided")
            return jsonify({
                'success': False,
                'message': 'Request body must be JSON'
            }), 400
        
        user_id = data.get('userId', '').strip()
        password = data.get('password', '').strip()
        
        if not user_id or not password:
            logger.warning(f"Student login: Missing credentials - userId={bool(user_id)}, password={bool(password)}")
            return jsonify({
                'success': False,
                'message': 'User ID and password are required'
            }), 400
        
        logger.info(f"Student login attempt: {user_id}")
        
        # Always try to fetch from MongoDB directly (bypass auth_service)
        try:
            from pymongo import MongoClient
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGODB_DATABASE', 'classroomassisstant')
            
            # Create a direct connection to get student data
            direct_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            direct_db = direct_client[db_name]
            student_collection = direct_db['student']
            
            # Try to find student in database
            student = student_collection.find_one({'user_id': user_id})
            if student:
                # Found in database - return real student data
                logger.info(f"✅ Student found in DB: {user_id} - {student.get('name', 'N/A')}")
                session_data = {
                    'userId': user_id,
                    'name': student.get('name', user_id),  # Use REAL name from DB
                    'role': 'student',
                    'preferredLanguage': student.get('preferred_language', 'english')
                }
                active_sessions[user_id] = session_data
                demo_token = 'demo_token_' + user_id + '_' + str(int(datetime.now().timestamp()))
                
                direct_client.close()
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': session_data,
                    'token': demo_token
                }), 200
            
            direct_client.close()
        except Exception as e:
            logger.warning(f"⚠️  Could not fetch from MongoDB: {str(e)}")
        
        # Fallback to demo mode if MongoDB not available
        logger.info(f"Student login (FALLBACK): {user_id}")
        demo_token = 'demo_token_' + user_id + '_' + str(int(datetime.now().timestamp()))
        
        # Generate a demo student name only as fallback
        demo_names = ['Arjun Kumar', 'Priya Singh', 'Ravi Patel', 'Anjali Sharma', 'Vikram Gupta', 'Neha Verma', 'Aditya Rao', 'Pooja Nair']
        demo_name = demo_names[hash(user_id) % len(demo_names)]
        
        session_data = {
            'userId': user_id,
            'name': demo_name,
            'role': 'student',
            'preferredLanguage': 'english'
        }
        active_sessions[user_id] = session_data
        
        return jsonify({
            'success': True,
            'message': 'Fallback login (MongoDB unavailable)',
            'user': session_data,
            'token': demo_token
        }), 200
        
        if status_code == 200:
            # Track active session
            session_data = result.get('user', {})
            session_data['loginTime'] = datetime.now().isoformat()
            active_sessions[user_id] = session_data
            
            # Track login history
            with login_history_lock:
                if user_id not in login_history:
                    login_history.add(user_id)
                    try:
                        with open(login_history_file, 'wb') as lf:
                            pickle.dump(login_history, lf)
                    except Exception as e:
                        logger.warning(f"Could not save login history: {str(e)}")
            
            logger.info(f"Student login successful: {user_id}")
        else:
            logger.warning(f"Student login failed: {user_id} - Status {status_code}")
        
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Student login error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500


@app.route('/api/teacher/start-class', methods=['POST'])
def teacher_start_class():
    """Generate a join code when teacher starts class"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            logger.warning("Start class: No authorization header")
            return jsonify({'success': False, 'message': 'Unauthorized - no token provided'}), 401

        token = auth_header.replace('Bearer ', '')
        
        if not token:
            logger.warning("Start class: Empty token")
            return jsonify({'success': False, 'message': 'Unauthorized - invalid token format'}), 401

        # ✅ DEVELOPMENT MODE: Accept mock tokens
        flask_env = os.environ.get('FLASK_ENV', 'development')
        if flask_env == 'development' and token.startswith('mock-'):
            logger.info(f"✅ Development mode: Accepting mock token")
            # Use a default demo teacher for mock auth
            email = 'demo.teacher@example.com'
            teacher = {
                'id': 'mock-teacher-id',
                'name': 'Demo Teacher',
                'email': email
            }
        else:
            # Verify token and extract payload
            token_result = auth_service.verify_token(token)
            
            if not token_result or not token_result.get('valid'):
                logger.warning(f"Start class: Invalid token - {token_result.get('message') if token_result else 'verification failed'}")
                return jsonify({'success': False, 'message': 'Unauthorized - invalid or expired token'}), 401

            # Get email from token payload
            email = token_result.get('payload', {}).get('email')
            
            if not email:
                logger.warning("Start class: No email in token")
                return jsonify({'success': False, 'message': 'Invalid token payload'}), 401

            # Get teacher by email from MongoDB
            teacher = auth_service.collection.find_one({'email': email})
            
            if not teacher:
                logger.warning(f"Start class: Teacher not found - {email}")
                return jsonify({'success': False, 'message': 'Teacher not found'}), 404

        data = request.json or {}
        subject = (data.get('subject') or 'General').strip()

        # Generate 6-char join code
        join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Store session
        session = {
            'teacherId': teacher.get('id'),
            'teacherName': teacher.get('name'),
            'subject': subject,
            'joinCode': join_code,
            'isActive': True,
            'createdAt': datetime.utcnow().isoformat(),
            'students': []
        }
        active_teacher_sessions[join_code] = session

        logger.info(f"✅ Class started - Code: {join_code}, Teacher: {teacher.get('name')}, Subject: {subject}")
        return jsonify({'success': True, 'joinCode': join_code}), 200
    
    except Exception as e:
        logger.error(f"❌ Error starting class: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Failed to start class: {str(e)}'}), 500


@app.route('/api/teacher/stop-class', methods=['POST'])
def teacher_stop_class():
    """Stop a class and invalidate the join code"""
    try:
        data = request.json or {}
        join_code = (data.get('joinCode') or '').strip().upper()

        if not join_code:
            logger.warning("Stop class: No join code provided")
            return jsonify({'success': False, 'message': 'Join code required'}), 400

        if join_code not in active_teacher_sessions:
            logger.warning(f"Stop class: Join code not found - {join_code}")
            return jsonify({'success': False, 'message': 'Join code not found'}), 404

        # Get session info before deleting
        session = active_teacher_sessions[join_code]
        num_students = len(session.get('students', []))
        
        # Stop the class
        del active_teacher_sessions[join_code]
        
        # Also clear broadcast content for this class
        if join_code in class_content_store:
            del class_content_store[join_code]
        
        logger.info(f"✅ Class stopped - Code: {join_code}, Students: {num_students}")
        return jsonify({'success': True, 'message': 'Class stopped'}), 200
    
    except Exception as e:
        logger.error(f"Stop class error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Failed to stop class: {str(e)}'}), 500

@app.route('/api/student/check-class-active', methods=['GET'])
def check_class_active():
    """Check if a class is still active (not stopped by teacher)"""
    try:
        join_code = request.args.get('joinCode', '').strip().upper()
        
        if not join_code:
            logger.warning("Check class active: No join code provided")
            return jsonify({'success': False, 'message': 'Join code required'}), 400
        
        # If join code exists in active sessions, class is active
        is_active = join_code in active_teacher_sessions
        
        return jsonify({'success': True, 'isActive': is_active}), 200
    
    except Exception as e:
        logger.error(f"Check class active error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/student/join', methods=['POST'])
def student_join():
    """Student joins a class using join code"""
    try:
        data = request.json or {}
        student_id = (data.get('studentId') or '').strip()
        join_code = (data.get('joinCode') or '').strip().upper()

        if not student_id or not join_code:
            logger.warning(f"Student join: Missing params - studentId={bool(student_id)}, joinCode={bool(join_code)}")
            return jsonify({'success': False, 'message': 'studentId and joinCode are required'}), 400

        # Check if join code exists and is active
        session = active_teacher_sessions.get(join_code)
        if not session or not session.get('isActive'):
            logger.warning(f"Student join: Invalid join code - {join_code}")
            return jsonify({'success': False, 'message': 'Invalid or expired join code'}), 400

        # Check if student already joined
        for s in session.get('students', []):
            if s.get('studentId') == student_id:
                logger.info(f"Student {student_id} already joined {join_code}")
                return jsonify({'success': True, 'message': 'Already joined'}), 200

        # Add student to session
        student_entry = {
            'studentId': student_id,
            'joinedAt': datetime.utcnow().isoformat()
        }
        session['students'].append(student_entry)
        
        logger.info(f"✅ Student {student_id} joined class {join_code}")

        return jsonify({
            'success': True,
            'teacherId': session.get('teacherId'),
            'teacherName': session.get('teacherName'),
            'subject': session.get('subject')
        }), 200
    
    except Exception as e:
        logger.error(f"Student join error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Failed to join: {str(e)}'}), 500


# Dictionary to store current speech/content for each class session
class_content_store = {}


@app.route('/api/teacher/broadcast-speech', methods=['POST'])
def broadcast_speech():
    """Teacher broadcasts speech/text to all connected students"""
    try:
        data = request.json or {}
        join_code = data.get('joinCode', '').strip().upper()
        english_text = data.get('englishText', '').strip()
        bodo_translation = data.get('bodoTranslation', '').strip()
        mizo_translation = data.get('mizoTranslation', '').strip()
        
        if not join_code:
            logger.warning("Broadcast: No join code provided")
            return jsonify({'success': False, 'message': 'Join code required'}), 400
        
        if not english_text:
            logger.warning("Broadcast: No English text provided")
            return jsonify({'success': False, 'message': 'English text required'}), 400
        
        # Verify join code exists
        if join_code not in active_teacher_sessions:
            logger.warning(f"Broadcast: Invalid join code - {join_code}")
            return jsonify({'success': False, 'message': 'Invalid join code'}), 404
        
        # Store the current content for this class
        class_content_store[join_code] = {
            'englishText': english_text,
            'bodoTranslation': bodo_translation,
            'mizoTranslation': mizo_translation,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Broadcast to {join_code}: '{english_text[:40]}...'")
        return jsonify({'success': True, 'message': 'Broadcast successful'}), 200
    
    except Exception as e:
        logger.error(f"❌ Broadcast error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Broadcast failed: {str(e)}'}), 500

@app.route('/api/student/get-content', methods=['GET'])
def get_class_content():
    """Students fetch the current class content"""
    try:
        join_code = request.args.get('joinCode', '').strip().upper()
        
        if not join_code:
            logger.warning("Get content: No join code provided")
            return jsonify({'success': False, 'message': 'Join code required'}), 400
        
        # Get content for this class
        content = class_content_store.get(join_code)
        
        if not content:
            return jsonify({
                'success': True,
                'content': {
                    'englishText': '',
                    'bodoTranslation': '',
                    'mizoTranslation': '',
                    'timestamp': ''
                }
            }), 200
        
        return jsonify({'success': True, 'content': content}), 200
    
    except Exception as e:
        logger.error(f"❌ Get content error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Failed to get content: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"=" * 50)
    logger.info(f"Starting Classroom Assistant API")
    logger.info(f"Environment: {flask_env}")
    logger.info(f"Port: {port}")
    logger.info(f"Debug: {debug_mode}")
    logger.info(f"Loaded {len(getattr(translation_service, 'translation_db', {}).get('english', {}))} translations")
    logger.info(f"=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
