print("🔥 App is starting...")
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# ================= IMPORT BLUEPRINTS =================
from routes.auth import auth_bp, google_bp   # ✅ include google_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp

# ================= CREATE APP =================
app = Flask(__name__)

# 🔐 SECRET KEY (IMPORTANT for OAuth)
app.secret_key = os.getenv("SECRET_KEY", "super-secret")

# ================= CORS =================
CORS(app, supports_credentials=True)

# ================= GLOBAL HEADERS =================
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

# ================= HANDLE PREFLIGHT =================
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return '', 200

# ================= REGISTER BLUEPRINTS =================

# 🔐 AUTH (NORMAL LOGIN/REGISTER)
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# 🌐 GOOGLE OAUTH (IMPORTANT PATH)
# app.register_blueprint(google_bp, url_prefix="/login")

# 📊 OTHER MODULES
app.register_blueprint(students_bp, url_prefix="/api/students")
app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
app.register_blueprint(marks_bp, url_prefix="/api/marks")

# ================= HOME =================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend running 🚀"
    })

# ================= TEST API =================
@app.route("/api/test")
def test():
    return {"status": "API working ✅"}

# ================= DEBUG ROUTES =================
@app.route("/routes")
def routes():
    return jsonify({
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })

# ================= DATABASE TEST =================
try:
    from utils.db import get_connection
except Exception as e:
    print("DB import error:", e)

@app.route("/test-db")
def test_db():
    try:
        db = get_connection()
        if db:
            db.close()
            return {"status": "DB connected ✅"}
        else:
            return {"status": "DB connection failed ❌"}
    except Exception as e:
        return {"error": str(e)}

# ================= ERROR HANDLERS =================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)