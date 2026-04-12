from flask import Flask, jsonify
from flask_cors import CORS
import os

# 🔥 IMPORT BLUEPRINTS
from routes.auth import auth_bp
from routes.students import students_bp   # ✅ USE THIS (FINAL)
from routes.attendance import attendance_bp
from routes.marks import marks_bp

# =========================================================
# 🚀 CREATE APP
# =========================================================
app = Flask(__name__)

# =========================================================
# 🌐 CORS CONFIG
# =========================================================
CORS(app, resources={r"/*": {"origins": "*"}})

# =========================================================
# 📌 REGISTER BLUEPRINTS
# =========================================================
app.register_blueprint(auth_bp, url_prefix="/auth")

# ✅ IMPORTANT: students_bp already has /students inside it
app.register_blueprint(students_bp)

# (Optional - keep if used elsewhere)
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(marks_bp, url_prefix="/marks")

# ❌ REMOVE THIS (CAUSE OF BUGS)
# app.register_blueprint(student_bp, url_prefix="/students")

# =========================================================
# 🏠 HOME ROUTE
# =========================================================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend running 🚀"
    })

# =========================================================
# 🔍 DEBUG ROUTES
# =========================================================
@app.route("/routes")
def routes():
    return jsonify({
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })

# =========================================================
# 🧪 DB TEST ROUTE
# =========================================================
from utils.db import get_connection

@app.route("/test-db")
def test_db():
    try:
        db = get_connection()
        if db:
            return {"status": "DB connected ✅"}
        else:
            return {"status": "DB connection failed ❌"}
    except Exception as e:
        return {"error": str(e)}

# =========================================================
# ❌ ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# =========================================================
# 🚀 RUN SERVER
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)