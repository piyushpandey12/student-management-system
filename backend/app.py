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


# =========================================================
# 🌐 CORS (FINAL FIX)
# =========================================================
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},   # 🔥 allow all (safe for now)
    supports_credentials=True
)

# 🔥 FORCE HEADERS (CRITICAL FOR VERCEL)
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


# 🔥 HANDLE PREFLIGHT (MOST IMPORTANT FIX)
@app.route("/api/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    return "", 200


# =========================================================
# 📦 IMPORT BLUEPRINTS (MUST BE BEFORE REGISTER)
# =========================================================
try:
    from backend.routes.auth import auth_bp
    from backend.routes.students import students_bp
    from backend.routes.attendance import attendance_bp
    from backend.routes.marks import marks_bp

    logger.info("✅ Blueprints imported")

except Exception as e:
    logger.error("❌ Import Error: %s", str(e))
    raise


# =========================================================
# 📌 REGISTER BLUEPRINTS
# =========================================================
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(students_bp, url_prefix="/api/students")
app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
app.register_blueprint(marks_bp, url_prefix="/api/marks")

logger.info("✅ Blueprints registered")


# =========================================================
# 🗄️ INIT DB (FLASK 3 SAFE)
# =========================================================
def setup_db():
    try:
        init_db_pool()
        logger.info("✅ DB Pool initialized")
    except Exception as e:
        logger.error("❌ DB Init Failed: %s", str(e))
        raise

setup_db()


# =========================================================
# 📌 ROUTES
# =========================================================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend running 🚀"
    })


@app.route("/api/test")
def test():
    return jsonify({"status": "API working"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


# =========================================================
# 🔍 DB TEST
# =========================================================
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

    except Exception:
        if conn:
            conn.rollback()

        logger.error("DB Test Error")

        return jsonify({
            "status": "error",
            "message": "Database error"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


# =========================================================
# 📌 DEBUG ROUTES
# =========================================================
@app.route("/routes")
def routes():
    return jsonify({
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })


# =========================================================
# ⚠️ ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "Route not found"
    }), 404


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("🔥 Unhandled Exception: %s", str(e))

    return jsonify({
        "status": "error",
        "message": "Something went wrong"
    }), 500


# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )