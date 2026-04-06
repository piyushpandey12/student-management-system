from flask import Flask, jsonify
from flask_cors import CORS
import os

# 🔥 IMPORT ROUTES
from routes.auth import auth_bp
from routes.student import student_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp

app = Flask(__name__)


# =========================================================
# 🌐 CORS CONFIG (SAFE + FLEXIBLE)
# =========================================================
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "https://your-frontend-domain.com"
        ]
    }
})


# =========================================================
# 📌 REGISTER BLUEPRINTS
# =========================================================
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(student_bp, url_prefix="/students")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(marks_bp, url_prefix="/marks")


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
# ❌ GLOBAL ERROR HANDLER (OPTIONAL BUT GOOD)
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

    # Debug only for local development
    debug = os.environ.get("FLASK_ENV") == "development"

    app.run(host="0.0.0.0", port=port, debug=debug)