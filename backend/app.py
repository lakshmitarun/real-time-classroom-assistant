from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime
import logging
import traceback
import os

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
            "supports_credentials": False,
            "max_age": 86400
        }
    },
    origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        FRONTEND_URL,
        "*.vercel.app"
    ],
    supports_credentials=False
)

logger.info("🔧 CORS Configuration:")
logger.info(f"  Frontend URL: {FRONTEND_URL}")
logger.info(f"  Allowed Origins: http://localhost:3001, {FRONTEND_URL}, *.vercel.app")

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

        # ✅ DEMO LOGIN (replace with DB later)
        token = f"demo_{user_id}_{int(datetime.now().timestamp())}"

        logger.info(f"✅ Student login successful: {user_id}")
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "userId": user_id,
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
