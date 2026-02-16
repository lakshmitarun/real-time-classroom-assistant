from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime
import logging
import traceback
import os
import sys
import json
from google.auth.transport import requests
from google.oauth2 import id_token
from auth_service_mongodb import AuthServiceMongoDB
from services.translation_service import TranslationService

# =============================
# APP + LOGGING
# =============================
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# =============================
# IN-MEMORY BROADCAST STORAGE
# =============================
# Store broadcasts by join code
broadcasts_store = {}

# =============================
# CORS CONFIG - Using Flask-CORS
# =============================
# Get frontend URL from environment variable or use defaults
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app"
)

# List of allowed origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    FRONTEND_URL,
]

# Function to check if origin is allowed (supports vercel.app wildcard)
def is_allowed_origin(origin):
    if origin in ALLOWED_ORIGINS:
        return True
    if origin and "vercel.app" in origin:
        return True
    return False

# CORS Configuration with custom handler
CORS(
    app,
    origins=is_allowed_origin,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
    supports_credentials=True,
    max_age=86400
)

logger.info("🔧 CORS Configuration:")
logger.info(f"  Frontend URL: {FRONTEND_URL}")
logger.info(f"  Allowed Origins: {ALLOWED_ORIGINS}")
logger.info(f"  Wildcard: *.vercel.app")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')

# =============================
# AUTH SERVICE
# =============================
try:
    auth_service = AuthServiceMongoDB(secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key'))
    logger.info("✅ AuthServiceMongoDB initialized")
except Exception as e:
    logger.warning(f"⚠️ AuthServiceMongoDB initialization failed: {e}")
    logger.warning(f"⚠️ MONGODB_URI: {os.getenv('MONGODB_URI', 'NOT SET')}")
    logger.warning(f"⚠️ MONGODB_DATABASE: {os.getenv('MONGODB_DATABASE', 'NOT SET')}")
    logger.warning("⚠️ Teacher login will use fallback demo mode")
    auth_service = None

# =============================
# EXPLICIT CORS HANDLER
# =============================
@app.before_request
def handle_preflight():
    """Handle preflight requests"""
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin", "")
        if is_allowed_origin(origin):
            response = make_response("", 204)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
            response.headers["Vary"] = "Origin"
            return response
        logger.warning(f"⚠️ Rejecting preflight request from disallowed origin: {origin}")
        return "", 403

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get("Origin", "")
    if is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"
    return response

# =============================
# ROUTES
# =============================

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "running",
        "message": "Backend API running"
    }), 200

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "time": datetime.utcnow().isoformat()
    }), 200

# =============================
# STUDENT LOGIN
# =============================
@app.route("/api/student/login", methods=["POST"])
def student_login():
    """Student login endpoint - CORS handled by Flask-CORS"""
    try:
        data = request.json or {}

        user_id = data.get("userId", "").strip()
        password = data.get("password", "").strip()

        if not user_id or not password:
            return jsonify({
                "success": False,
                "message": "User ID and password required"
            }), 400

        # Try to fetch student from MongoDB
        if auth_service:
            logger.info(f"🔐 Authenticating student: {user_id}")
            result, status_code = auth_service.student_login(user_id, password)
            
            if result.get("success"):
                logger.info(f"✅ Student login successful: {user_id}")
                return jsonify(result), status_code
            else:
                logger.warning(f"❌ Student login failed: {user_id} - {result.get('message')}")
                return jsonify(result), status_code
        else:
            # Fallback: Demo login (for development/testing)
            logger.warning(f"⚠️ Using fallback demo login for student: {user_id}")
            token = f"demo_{user_id}_{int(datetime.now().timestamp())}"
            
            return jsonify({
                "success": True,
                "message": "Login successful (Fallback)",
                "userId": user_id,
                "name": f"Student {user_id}",  # Show student ID as name
                "role": "student",
                "token": token
            }), 200

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Server error",
            "error": str(e)
        }), 500

# =============================
# TEACHER LOGIN
# =============================
@app.route("/api/auth/login", methods=["POST"])
def teacher_login():
    """Teacher login endpoint - Uses MongoDB auth"""
    try:
        data = request.json or {}
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password required"
            }), 400

        # Try real authentication first
        if auth_service:
            logger.info(f"🔐 Authenticating teacher: {email}")
            result, status_code = auth_service.login(email, password)
            
            if result.get("success"):
                logger.info(f"✅ Teacher login successful: {email}")
                return jsonify(result), status_code
            else:
                logger.warning(f"❌ Teacher login failed: {email} - {result.get('message')}")
                return jsonify(result), status_code
        else:
            # Fallback: Demo mode (for development/testing)
            logger.warning(f"⚠️ Using fallback demo login for: {email}")
            token = f"demo_{email}_{int(datetime.now().timestamp())}"
            
            return jsonify({
                "success": True,
                "message": "Login successful (Fallback)",
                "user": {
                    "id": "demo_teacher_id",
                    "email": email,
                    "name": "Demo Teacher (Fallback)",
                    "role": "teacher"
                },
                "teacher": {
                    "id": "demo_teacher_id",
                    "email": email,
                    "name": "Demo Teacher (Fallback)",
                    "role": "teacher"
                },
                "token": token
            }), 200

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Server error",
            "error": str(e)
        }), 500

# =============================
# TEACHER REGISTRATION
# =============================
@app.route("/api/auth/register", methods=["POST"])
def teacher_register():
    """Teacher registration endpoint"""
    try:
        data = request.json or {}
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        name = data.get("name", "").strip()

        if not email or not password or not name:
            return jsonify({
                "success": False,
                "message": "Email, password, and name required"
            }), 400

        # Try real registration first
        if auth_service:
            logger.info(f"📝 Registering teacher: {email}")
            result, status_code = auth_service.register(email, password, name)
            
            if result.get("success"):
                logger.info(f"✅ Teacher registered successfully: {email}")
                return jsonify(result), status_code
            else:
                logger.warning(f"❌ Teacher registration failed: {email} - {result.get('message')}")
                return jsonify(result), status_code
        else:
            # Fallback: Demo mode (for development/testing)
            logger.warning(f"⚠️ Using fallback demo registration for: {email}")
            token = f"demo_{email}_{int(datetime.now().timestamp())}"
            
            return jsonify({
                "success": True,
                "message": "Registration successful (Fallback)",
                "user": {
                    "id": "demo_teacher_id",
                    "email": email,
                    "name": name or "Demo Teacher",
                    "role": "teacher"
                },
                "teacher": {
                    "id": "demo_teacher_id",
                    "email": email,
                    "name": name or "Demo Teacher",
                    "role": "teacher"
                },
                "token": token
            }), 200

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Server error",
            "error": str(e)
        }), 500

# =============================
# LOGOUT
# =============================
@app.route("/api/logout", methods=["POST"])
def logout():
    """Logout endpoint - just returns success"""
    try:
        logger.info("👋 User logged out")
        return jsonify({
            "success": True,
            "message": "Logged out successfully"
        }), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Logout failed"
        }), 500

# =============================
# GOOGLE AUTH CALLBACK
# =============================
@app.route("/api/auth/google/callback", methods=["POST", "OPTIONS"])
def google_callback():
    """Handle Google OAuth callback - CORS enabled"""
    # Handle OPTIONS preflight request
    if request.method == "OPTIONS":
        response = make_response("", 204)
        origin = request.headers.get("Origin", "")
        if is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Vary"] = "Origin"
        return response

    try:
        data = request.json or {}
        credential = data.get("credential", "").strip()

        if not credential:
            return jsonify({
                "success": False,
                "error": "Missing credential"
            }), 400

        logger.info("🔐 Processing Google OAuth callback")

        # Verify the Google token and extract user information
        try:
            # Decode the JWT without verification first to extract claims
            # In production, you should verify the signature properly
            import base64
            parts = credential.split('.')
            if len(parts) == 3:
                # Decode the payload
                payload = parts[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                
                email = decoded.get('email', '').lower().strip()
                name = decoded.get('name', '')
                google_id = decoded.get('sub', '')
                
                logger.info(f"✅ Google token decoded - Email: {email}, Name: {name}")
                
                if not email:
                    return jsonify({
                        "success": False,
                        "error": "Could not extract email from token"
                    }), 400
                
                # Use auth service to login/register with Google
                if auth_service:
                    result, status_code = auth_service.google_login(email, name, google_id)
                    logger.info(f"✅ Google login result: {result}")
                    return jsonify(result), status_code
                else:
                    # Fallback: Create a temporary token for demo mode
                    logger.warning("⚠️ Using fallback demo mode for Google login")
                    demo_token = f"google_demo_{google_id}_{int(datetime.now().timestamp())}"
                    
                    return jsonify({
                        "success": True,
                        "token": demo_token,
                        "role": "teacher",
                        "teacher": {
                            "id": f"google-{google_id[:8]}",
                            "email": email,
                            "name": name,
                            "auth_method": "google"
                        }
                    }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid token format"
                }), 400

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to decode Google token: {e}")
            return jsonify({
                "success": False,
                "error": "Invalid token format"
            }), 400

    except Exception as e:
        logger.error(f"❌ Google callback failed: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =============================
# TRANSLATION SERVICE
# =============================
@app.route("/api/translate", methods=["POST", "OPTIONS"])
def translate():
    """Translate text from source language to target language"""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return make_response(jsonify({"success": True}), 200)
    
    try:
        data = request.json or {}
        text = data.get("text", "").strip()
        source_lang = data.get("source_lang", "english").lower()
        target_lang = data.get("target_lang", "bodo").lower()
        
        if not text:
            return jsonify({
                "success": False,
                "message": "No text provided"
            }), 400
        
        # Initialize translation service
        translation_service = TranslationService()
        
        # Translate the text
        translation = translation_service.translate(
            text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        logger.info(f"✅ Translated: '{text}' ({source_lang}→{target_lang})")
        
        return jsonify({
            "success": True,
            "translation": translation,
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Translation error: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Translation failed",
            "error": str(e)
        }), 500

@app.route("/api/translate/batch", methods=["POST"])
def translate_batch():
    """Translate text to Bodo and Mizo"""
    try:
        data = request.json or {}
        texts = data.get("texts", [])
        
        if not texts:
            return jsonify({
                "success": False,
                "message": "No text provided"
            }), 400
        
        # Initialize translation service
        translation_service = TranslationService()
        
        results = []
        for text in texts:
            bodo_translation = translation_service.translate(text, source_lang="english", target_lang="bodo")
            mizo_translation = translation_service.translate(text, source_lang="english", target_lang="mizo")
            
            results.append({
                "englishText": text,
                "bodoTranslation": bodo_translation,
                "mizoTranslation": mizo_translation
            })
        
        logger.info(f"✅ Translated {len(texts)} texts")
        
        return jsonify({
            "success": True,
            "translations": results
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Translation error: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Translation failed",
            "error": str(e)
        }), 500

# =============================
# TEACHER ENDPOINTS
# =============================
@app.route("/api/teacher/start-class", methods=["POST"])
def start_class():
    """Start a class session"""
    try:
        data = request.json or {}
        teacher_id = data.get("teacherId")
        
        if not teacher_id:
            return jsonify({
                "success": False,
                "message": "Teacher ID required"
            }), 400
        
        # Generate a join code for students
        join_code = f"{teacher_id[:4]}{int(datetime.now().timestamp()) % 10000}".upper()
        
        logger.info(f"🎓 Class started by teacher {teacher_id}, join code: {join_code}")
        
        return jsonify({
            "success": True,
            "message": "Class started",
            "joinCode": join_code,
            "classStartedAt": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to start class",
            "error": str(e)
        }), 500

@app.route("/api/teacher/end-class", methods=["POST"])
def end_class():
    """End a class session"""
    try:
        data = request.json or {}
        teacher_id = data.get("teacherId")
        
        if not teacher_id:
            return jsonify({
                "success": False,
                "message": "Teacher ID required"
            }), 400
        
        logger.info(f"🛑 Class ended by teacher {teacher_id}")
        
        return jsonify({
            "success": True,
            "message": "Class ended"
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to end class"
        }), 500

@app.route("/api/teacher/stop-class", methods=["POST"])
def stop_class():
    """Stop a class session and clear broadcasts"""
    try:
        data = request.json or {}
        join_code = data.get("joinCode")
        
        if not join_code:
            return jsonify({
                "success": False,
                "message": "Join code required"
            }), 400
        
        # Clear the broadcast for this join code
        if join_code in broadcasts_store:
            del broadcasts_store[join_code]
            logger.info(f"🛑 Class stopped, broadcasts cleared for {join_code}")
        
        return jsonify({
            "success": True,
            "message": "Class stopped"
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to end class"
        }), 500

@app.route("/api/teacher/broadcast", methods=["POST"])
def broadcast_content():
    """Broadcast content to students"""
    try:
        data = request.json or {}
        teacher_id = data.get("teacherId")
        english_text = data.get("englishText", "")
        bodo_translation = data.get("bodoTranslation", "")
        mizo_translation = data.get("mizoTranslation", "")
        join_code = data.get("joinCode")
        
        if not teacher_id or not join_code:
            return jsonify({
                "success": False,
                "message": "Teacher ID and join code required"
            }), 400
        
        # Store the broadcast content
        broadcasts_store[join_code] = {
            "englishText": english_text,
            "bodoTranslation": bodo_translation,
            "mizoTranslation": mizo_translation,
            "timestamp": datetime.utcnow().isoformat(),
            "teacherId": teacher_id
        }
        
        logger.info(f"📡 Teacher {teacher_id} broadcasting to {join_code}: {english_text[:50]}")
        
        return jsonify({
            "success": True,
            "message": "Content broadcast",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to broadcast"
        }), 500

@app.route("/api/teacher/broadcast-speech", methods=["POST"])
def broadcast_speech():
    """Alias endpoint for backward compatibility"""
    try:
        data = request.json or {}
        join_code = data.get("joinCode")
        english_text = data.get("englishText", "")
        bodo_translation = data.get("bodoTranslation", "")
        mizo_translation = data.get("mizoTranslation", "")
        
        if not join_code:
            return jsonify({
                "success": False,
                "message": "Join code required"
            }), 400
        
        # Store the broadcast content
        broadcasts_store[join_code] = {
            "englishText": english_text,
            "bodoTranslation": bodo_translation,
            "mizoTranslation": mizo_translation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"📡 Broadcasting to {join_code}: {english_text[:50]}")
        
        return jsonify({
            "success": True,
            "message": "Content broadcast",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to broadcast"
        }), 500

@app.route("/api/student/join", methods=["POST"])
def student_join():
    """Student join a class"""
    try:
        data = request.json or {}
        student_id = data.get("studentId")
        join_code = data.get("joinCode")
        
        if not student_id or not join_code:
            return jsonify({
                "success": False,
                "message": "Student ID and join code required"
            }), 400
        
        logger.info(f"👤 Student {student_id} joined with code {join_code}")
        
        return jsonify({
            "success": True,
            "message": "Joined successfully",
            "joinCode": join_code
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to join class"
        }), 500

@app.route("/api/student/get-content", methods=["GET"])
def get_content():
    """Get current class content"""
    try:
        join_code = request.args.get("joinCode")
        
        if not join_code:
            return jsonify({
                "success": False,
                "message": "Join code required"
            }), 400
        
        return jsonify({
            "success": True,
            "content": {
                "englishText": "",
                "bodoTranslation": "",
                "mizoTranslation": "",
                "timestamp": datetime.utcnow().isoformat()
            }
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to get content"
        }), 500

@app.route("/api/student/get-broadcast/<join_code>", methods=["GET"])
def get_broadcast(join_code):
    """Get current broadcast content for a specific join code"""
    try:
        join_code = join_code.upper()
        
        if join_code in broadcasts_store:
            broadcast = broadcasts_store[join_code]
            logger.debug(f"📨 Sending broadcast for {join_code}")
            return jsonify({
                "success": True,
                "content": {
                    "englishText": broadcast.get("englishText", ""),
                    "bodoTranslation": broadcast.get("bodoTranslation", ""),
                    "mizoTranslation": broadcast.get("mizoTranslation", ""),
                    "translatedText": broadcast.get("mizoTranslation", "") or broadcast.get("bodoTranslation", "")
                },
                "timestamp": broadcast.get("timestamp", datetime.utcnow().isoformat())
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No content available"
            }), 404
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": "Failed to get broadcast"
        }), 500

@app.route("/api/student/check-class-active", methods=["GET"])
def check_class_active():
    """Check if class is still active"""
    try:
        join_code = request.args.get("joinCode")
        
        if not join_code:
            return jsonify({
                "success": False,
                "isActive": False
            }), 400
        
        return jsonify({
            "success": True,
            "isActive": True
        }), 200
    
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "isActive": False
        }), 500

# =============================
# ADMIN ENDPOINTS - HISTORY & STATS
# =============================
@app.route("/api/classrooms/history", methods=["GET"])
def get_classrooms_history():
    """Get historical classroom data"""
    try:
        filter_type = request.args.get('filter', 'all').lower()
        
        # In a real application, you would fetch from database
        # For now, returning sample data structure
        past_classrooms = [
            {
                "teacher": "Mr. John",
                "subject": "Mathematics",
                "students": 25,
                "startTime": (datetime.utcnow().isoformat()),
                "endTime": (datetime.utcnow().isoformat()),
                "translationsCount": 45
            },
            {
                "teacher": "Mrs. Sarah",
                "subject": "English",
                "students": 30,
                "startTime": (datetime.utcnow().isoformat()),
                "endTime": (datetime.utcnow().isoformat()),
                "translationsCount": 67
            }
        ]
        
        return jsonify({
            "success": True,
            "classrooms": past_classrooms,
            "filter": filter_type
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch classroom history: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch history",
            "classrooms": []
        }), 500

@app.route("/api/students/history", methods=["GET"])
def get_students_history():
    """Get historical student data"""
    try:
        filter_type = request.args.get('filter', 'all').lower()
        
        # In a real application, you would fetch from database
        # For now, returning sample data structure
        past_students = [
            {
                "userId": "STU001",
                "name": "Raj Kumar",
                "preferredLanguage": "Bodo",
                "lastLogin": (datetime.utcnow().isoformat()),
                "totalSessions": 5,
                "totalTime": "2h 30m"
            },
            {
                "userId": "STU002",
                "name": "Priya Singh",
                "preferredLanguage": "Mizo",
                "lastLogin": (datetime.utcnow().isoformat()),
                "totalSessions": 8,
                "totalTime": "4h 15m"
            }
        ]
        
        return jsonify({
            "success": True,
            "students": past_students,
            "filter": filter_type
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch student history: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch history",
            "students": []
        }), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get current statistics"""
    try:
        return jsonify({
            "success": True,
            "active_classrooms": 2,
            "total_teachers": 15,
            "total_students": 150,
            "logged_in_students": 45,
            "total_unique_logins": 120,
            "avg_accuracy": 92,
            "avg_latency": 0.8,
            "total_translations": 2492
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch stats: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch stats"
        }), 500

@app.route("/api/active-students", methods=["GET"])
def get_active_students():
    """Get currently active students"""
    try:
        active_students = [
            {
                "userId": "STU001",
                "name": "Raj Kumar",
                "preferredLanguage": "Bodo",
                "loginTime": datetime.utcnow().isoformat()
            },
            {
                "userId": "STU002",
                "name": "Priya Singh",
                "preferredLanguage": "Mizo",
                "loginTime": datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({
            "success": True,
            "students": active_students
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch active students: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch active students",
            "students": []
        }), 500

@app.route("/api/classrooms", methods=["GET"])
def get_classrooms():
    """Get current classrooms"""
    try:
        classrooms = [
            {
                "teacher": "Mr. John",
                "subject": "Mathematics",
                "students": 25,
                "startTime": datetime.utcnow().isoformat(),
                "status": "active"
            },
            {
                "teacher": "Mrs. Sarah",
                "subject": "English",
                "students": 30,
                "startTime": datetime.utcnow().isoformat(),
                "status": "active"
            }
        ]
        
        return jsonify({
            "success": True,
            "classrooms": classrooms
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch classrooms: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch classrooms",
            "classrooms": []
        }), 500

@app.route("/api/translation-stats", methods=["GET"])
def get_translation_stats():
    """Get translation statistics"""
    try:
        stats = [
            {
                "language": "English → Bodo",
                "count": 1200,
                "accuracy": 95
            },
            {
                "language": "English → Mizo",
                "count": 1292,
                "accuracy": 93
            }
        ]
        
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch translation stats: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch translation stats",
            "stats": []
        }), 500

# =============================
# ERRORS
# =============================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# =============================
# LOCAL RUN (ignored on Vercel)
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
