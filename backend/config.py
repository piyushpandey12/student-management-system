# ================= IMPORTS =================
import os
import logging
from urllib.parse import urlparse, unquote

# =========================================================
# 🔧 LOGGING
# =========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# 📌 DATABASE CONFIG
# =========================================================
DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {}

try:
    if DATABASE_URL:
        # 🔧 Fix deprecated scheme (Render / old Heroku)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://", "postgresql://", 1
            )

        url = urlparse(DATABASE_URL)

        DB_CONFIG = {
            "host": url.hostname,
            "database": url.path.lstrip("/"),
            "user": url.username,
            "password": unquote(url.password) if url.password else "",
            "port": url.port or 5432,
            "sslmode": "require"
        }

        logger.info("✅ Using DATABASE_URL config")

    else:
        # =========================================================
        # 📌 LOCAL FALLBACK
        # =========================================================
        DB_CONFIG = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "student_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "sslmode": "prefer"
        }

        logger.warning("⚠️ Using LOCAL DB config")

    # =========================================================
    # 📌 VALIDATION
    # =========================================================
    required_keys = ["host", "database", "user", "port"]

    missing = [key for key in required_keys if not DB_CONFIG.get(key)]

    if missing:
        raise Exception(f"Missing DB config fields: {missing}")

    # ⚠️ Password can be empty (Google/managed DB edge cases)
    if DB_CONFIG.get("password") is None:
        DB_CONFIG["password"] = ""

    logger.info("✅ PostgreSQL config loaded successfully")

except Exception as e:
    logger.error("❌ DB CONFIG ERROR: %s", str(e))
    raise
