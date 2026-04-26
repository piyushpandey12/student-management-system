# ================= IMPORTS =================
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.utils.db import init_db_pool, get_connection, release_connection

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🔥 App is starting...")

# ================= CREATE APP =================
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret")

# ================= CORS =================
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=False
)

# ================= REQUEST LOGGING =================
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path}")

# ================= IMPORT BLUEPRINTS =================
try:
    from backend.routes.auth import auth_bp
    from backend.routes.students import students_bp
    from backend.routes.attendance import attendance_bp
    from backend.routes.marks import marks_bp
    from backend.routes.google_auth import google_auth_bp

    logger.info("✅ All Blueprints imported successfully")

except Exception as e:
    logger.error("❌ Import Error: %s", str(e))
    raise

# ================= INIT DB =================
try:
    init_db_pool()
    logger.info("✅ DB Pool initialized")
except Exception as e:
    logger.error("❌ DB Pool Init Failed: %s", str(e))

# ================= REGISTER BLUEPRINTS =================
try:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(marks_bp, url_prefix="/api/marks")

    # ✅ GOOGLE AUTH (FIXED — ONLY HERE)
    app.register_blueprint(google_auth_bp, url_prefix="/api/auth")

    logger.info("✅ All Blueprints registered successfully")

except Exception as e:
    logger.error("❌ Blueprint Register Error: %s", str(e))
    raise

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

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

# ================= DB TEST =================
@app.route("/test-db")
def test_db():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()[0]

        return jsonify({
            "status": "success",
            "time": str(current_time)
        })

    except Exception as e:
        if conn:
            conn.rollback()

        logger.error("DB Test Error: %s", str(e))

        return jsonify({
            "status": "error",
            "message": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

# ================= ROUTE LIST =================
@app.route("/routes")
def routes():
    return jsonify({
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })

# ================= GLOBAL ERROR HANDLER =================
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("🔥 Unhandled Exception: %s", str(e))

    return jsonify({
        "status": "error",
        "message": "Something went wrong"
    }), 500

# ================= 404 =================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "Route not found"
    }), 404

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV") == "development"

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )