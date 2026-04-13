from flask import Flask, jsonify
from flask_cors import CORS
import os

# ================= IMPORT BLUEPRINTS =================
from routes.auth import auth_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp

# ================= CREATE APP =================
app = Flask(__name__)

# ================= CORS (FINAL FIX) =================
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},  # allow all for API
    supports_credentials=True
)

# 🔥 HANDLE PREFLIGHT (VERY IMPORTANT)
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


# ================= REGISTER BLUEPRINTS =================
app.register_blueprint(auth_bp, url_prefix="/api/auth")
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
from utils.db import get_connection

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)