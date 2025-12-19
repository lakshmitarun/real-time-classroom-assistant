
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
import pickle
from threading import Lock
from dotenv import load_dotenv
from services.translation_service import TranslationService
from services.speech_service import SpeechService
from auth_service_supabase import AuthService, token_required
from supabase_config import get_supabase
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from datetime import datetime
import random
import string

load_dotenv()

app = Flask(__name__)
# Configure CORS to allow frontend on all development and production URLs
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3001",
            "http://localhost:3000",
            "http://localhost:5000",
            "https://kill-project.vercel.app",  # Frontend Vercel URL
            "https://*.vercel.app",  # All Vercel apps
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize services
translation_service = TranslationService()
speech_service = SpeechService()
auth_service = AuthService(secret_key=os.getenv('JWT_SECRET_KEY', 'classroom-assistant-secret-key'))
supabase = get_supabase()
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')

# Log OAuth configuration
if GOOGLE_CLIENT_ID:
    print(f"✅ Google OAuth configured: {GOOGLE_CLIENT_ID[:20]}...")
else:
    print("⚠️ WARNING: GOOGLE_CLIENT_ID not set!")


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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Classroom Assistant API is running',
        'version': '1.0.0'
    })

# ============ AUTHENTICATION ENDPOINTS ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        result, status_code = auth_service.register(email, password, name)
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        result, status_code = auth_service.login(email, password)
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/google/callback', methods=['POST'])
def google_callback():
    """Handle Google OAuth callback - frontend sends Google token"""
    try:
        data = request.json or {}

        # Accept either a client-verified ID token (credential) or legacy { email, name, id }
        credential = data.get('credential') or data.get('id_token')
        if credential:
            if not GOOGLE_CLIENT_ID:
                return jsonify({'error': 'Server misconfigured: GOOGLE_CLIENT_ID not set'}), 500
            try:
                idinfo = id_token.verify_oauth2_token(credential, grequests.Request(), GOOGLE_CLIENT_ID)
            except ValueError as e:
                return jsonify({'error': f'Invalid ID token: {str(e)}'}), 400

            email = idinfo.get('email', '').strip()
            name = idinfo.get('name', '') or idinfo.get('given_name', '')
            google_id = idinfo.get('sub', '')

            if not email or not google_id:
                return jsonify({'error': 'ID token missing required fields'}), 400

            result, status_code = auth_service.google_login(email, name, google_id)
            return jsonify(result), status_code

        # Fallback: legacy payload
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        google_id = data.get('id', '').strip()

        if not email or not google_id:
            return jsonify({'error': 'Email and Google ID are required'}), 400

        result, status_code = auth_service.google_login(email, name, google_id)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    """Verify if JWT token is valid"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        email = auth_service.verify_token(token)
        if not email:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        teacher = auth_service.get_teacher(email)
        return jsonify({
            'valid': True,
            'teacher': teacher
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teacher/profile', methods=['GET'])
def get_teacher_profile():
    """Get current teacher profile (requires auth)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        email = auth_service.verify_token(token)
        if not email:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        teacher = auth_service.get_teacher(email)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        return jsonify(teacher), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'english')
        target_lang = data.get('target_lang', 'bodo')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        translation = translation_service.translate(text, source_lang, target_lang)
        
        return jsonify({
            'source_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'translation': translation,
            'confidence': 0.95
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate/batch', methods=['POST'])
def translate_batch():
    try:
        data = request.json
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'english')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        translations = {
            'bodo': translation_service.translate(text, source_lang, 'bodo'),
            'mizo': translation_service.translate(text, source_lang, 'mizo'),
            'english': translation_service.translate(text, source_lang, 'english')
        }
        
        return jsonify({
            'source_text': text,
            'source_lang': source_lang,
            'translations': translations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speech/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'english')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        audio_url = speech_service.text_to_speech(text, language)
        
        return jsonify({
            'text': text,
            'language': language,
            'audio_url': audio_url
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        data = request.json
        user_id = data.get('userId', '').strip()
        
        if user_id in active_sessions:
            del active_sessions[user_id]
            return jsonify({
                'success': True,
                'message': 'Logged out successfully'
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Session not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }), 500

@app.route('/api/active-students', methods=['GET'])
def get_active_students():
    return jsonify({
        'count': len(active_sessions),
        'students': list(active_sessions.values())
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    with login_history_lock:
        total_unique_logins = len(login_history)
    return jsonify({
        'active_classrooms': 12,
        'total_teachers': 45,
        'total_students': 890,
        'logged_in_students': len(active_sessions),
        'total_unique_logins': total_unique_logins,
        'avg_accuracy': 94.5,
        'avg_latency': 1.8,
        'total_translations': 15420
    })

@app.route('/api/student/login', methods=['POST'])
def student_login():
    try:
        data = request.json
        user_id = data.get('userId', '').strip()
        password = data.get('password', '').strip()
        
        if not user_id or not password:
            return jsonify({
                'success': False,
                'message': 'User ID and password are required'
            }), 400
        
        # Load student logins from CSV
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'student_logins.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'message': 'Login database not found'
            }), 500
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stored_user_id = row.get('user_id', '').strip()
                stored_password = row.get('password', '').strip()
                if stored_user_id == user_id and stored_password == password:
                    # Track active session
                    from datetime import datetime
                    session_data = {
                        'userId': row.get('user_id', '').strip(),
                        'name': row.get('name', '').strip(),
                        'role': row.get('role', '').strip(),
                        'preferredLanguage': row.get('preferred_language', '').strip(),
                        'loginTime': datetime.now().isoformat()
                    }
                    active_sessions[user_id] = session_data
                    # Track login history
                    with login_history_lock:
                        if user_id not in login_history:
                            login_history.add(user_id)
                            with open(login_history_file, 'wb') as lf:
                                pickle.dump(login_history, lf)
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': session_data
                    }), 200
        
        return jsonify({
            'success': False,
            'message': 'Invalid user ID or password'
        }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500


@app.route('/api/teacher/start-class', methods=['POST'])
def teacher_start_class():
    """Generate a join code when teacher starts class"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        email = auth_service.verify_token(token)
        if not email:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        teacher = auth_service.get_teacher(email)
        if not teacher:
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

        return jsonify({'success': True, 'joinCode': join_code}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to start class: {str(e)}'}), 500


@app.route('/api/teacher/stop-class', methods=['POST'])
def teacher_stop_class():
    """Stop a class and invalidate the join code"""
    try:
        data = request.json or {}
        join_code = (data.get('joinCode') or '').strip().upper()

        if join_code in active_teacher_sessions:
            del active_teacher_sessions[join_code]
            return jsonify({'success': True, 'message': 'Class stopped'}), 200

        return jsonify({'success': False, 'message': 'Join code not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to stop class: {str(e)}'}), 500


@app.route('/api/student/join', methods=['POST'])
def student_join():
    """Student joins a class using join code"""
    try:
        data = request.json or {}
        student_id = (data.get('studentId') or '').strip()
        join_code = (data.get('joinCode') or '').strip().upper()

        if not student_id or not join_code:
            return jsonify({'success': False, 'message': 'studentId and joinCode are required'}), 400

        # Check if join code exists and is active
        session = active_teacher_sessions.get(join_code)
        if not session or not session.get('isActive'):
            return jsonify({'success': False, 'message': 'Invalid or expired join code'}), 400

        # Check if student already joined
        for s in session.get('students', []):
            if s.get('studentId') == student_id:
                return jsonify({'success': True, 'message': 'Already joined'}), 200

        # Add student to session
        student_entry = {
            'studentId': student_id,
            'joinedAt': datetime.utcnow().isoformat()
        }
        session['students'].append(student_entry)

        return jsonify({
            'success': True,
            'teacherId': session.get('teacherId'),
            'teacherName': session.get('teacherName'),
            'subject': session.get('subject')
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to join: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
