from flask import request, make_response
import logging

logger = logging.getLogger(__name__)

def setup_cors(app):

    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app",
    ]

    def is_allowed(origin):
        return origin in ALLOWED_ORIGINS or (origin and "vercel.app" in origin)

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            origin = request.headers.get("Origin")
            if not is_allowed(origin):
                return "", 403

            response = make_response("", 204)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Vary"] = "Origin"
            return response

    @app.after_request
    def add_headers(response):
        origin = request.headers.get("Origin")
        if is_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        return response

    return app
