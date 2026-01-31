from flask import Flask, request, jsonify, make_response
from datetime import datetime
import logging
import traceback

# =============================
# APP + LOGGING
# =============================
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================
# CORS CONFIG (ONE PLACE ONLY)
# =============================
ALLOWED_ORIGINS = [
    "http://localhost:3001",   # frontend local
    "http://127.0.0.1:3001",
    "https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app"
]

def is_allowed_origin(origin):
    if not origin:
        return False
    if origin in ALLOWED_ORIGINS:
        return True
    if "vercel.app" in origin:
        return True
    return False

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")

        if not is_allowed_origin(origin):
            return "", 403

        response = make_response("", 204)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Vary"] = "Origin"
        return response

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin and is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"

    if request.path.startswith("/api/"):
        response.headers["Content-Type"] = "application/json"

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
