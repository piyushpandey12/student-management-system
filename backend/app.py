print("🔥 App is starting...")

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# ================= CREATE APP =================
app = Flask(__name__)

# 🔐 SECRET KEY
app.secret_key = os.getenv("SECRET_KEY", "super-secret")

# ================= CORS (FIXED) =================
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True
)

# ❌ REMOVE this (causes CORS conflicts)
# @app.after_request ...

# ================= HANDLE PREFLIGHT =================
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return '', 200


# ================= SAFE IMPORTS =================
try:
    from backend.routes.auth import auth_bp, google_bp
    from backend.routes.students import students_bp
    from backend.routes.attendance import attendance_bp
    from backend.routes.marks import marks_bp

    print("✅ Blueprints imported successfully")
except Exception as e:
    print("❌ Import Error:", e)
    raise e


# ================= REGISTER BLUEPRINTS =================
try:
    # 🔐 AUTH APIs
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # 🌐 GOOGLE OAUTH
    app.register_blueprint(google_bp, url_prefix="/login")

    # 📊 MODULES
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(marks_bp, url_prefix="/api/marks")

    print("✅ Blueprints registered successfully")

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
    return jsonify({"status": "API working ✅"})


@app.route("/routes")
def routes():
    return jsonify({
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })


# ================= ERROR HANDLERS =================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))   # ✅ IMPORTANT FOR RENDER
    app.run(host="0.0.0.0", port=port, debug=True)