from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime
import logging
import traceback
import os
from auth_service_mongodb import AuthServiceMongoDB

# =============================
# APP + LOGGING
# =============================
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# =============================
# CORS CONFIG - Using Flask-CORS
# =============================
# Get frontend URL from environment variable or use defaults
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app"
)

# CORS Configuration
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3001",
                "http://127.0.0.1:3001",
                FRONTEND_URL,
                "*.vercel.app"  # Allow all vercel.app subdomains
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,  # ✅ Enable credentials support
            "max_age": 86400
        }
    },
    origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        FRONTEND_URL,
        "*.vercel.app"
    ],
    supports_credentials=True  # ✅ Enable credentials support
)

logger.info("🔧 CORS Configuration:")
logger.info(f"  Frontend URL: {FRONTEND_URL}")
logger.info(f"  Allowed Origins: http://localhost:3001, {FRONTEND_URL}, *.vercel.app")

# =============================
# AUTH SERVICE
# =============================
try:
    auth_service = AuthServiceMongoDB(secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key'))
    logger.info("✅ AuthServiceMongoDB initialized")
except Exception as e:
    logger.warning(f"⚠️ AuthServiceMongoDB initialization failed: {e}")
    logger.warning("⚠️ Teacher login will use fallback demo mode")
    auth_service = None

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
