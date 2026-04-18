print("🔥 App is starting...")

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# ================= CREATE APP =================
app = Flask(__name__)
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

# ================= SAFE IMPORTS =================
try:
    from routes.auth import auth_bp
    from routes.students import students_bp
    from routes.attendance import attendance_bp
    from routes.marks import marks_bp
    print("✅ Blueprints imported")
except Exception as e:
    print("❌ Import Error:", e)
    raise e

# ================= REGISTER BLUEPRINTS =================
try:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(marks_bp, url_prefix="/api/marks")
except Exception as e:
    print("❌ Blueprint Register Error:", e)
    raise e

# ================= ROUTES =================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend running 🚀"
    })

@app.route("/api/test")
def test():
    return {"status": "API working ✅"}

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