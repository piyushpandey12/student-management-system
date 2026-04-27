import os
import logging
from urllib.parse import urlparse, unquote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {}

try:
    if DATABASE_URL:

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

        logger.info(f"✅ DATABASE_URL detected → {DB_CONFIG['host']}")

    else:
        DB_CONFIG = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "student_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "sslmode": "prefer"
        }

        logger.warning("⚠️ Using LOCAL DB config")

    # 🔍 VALIDATION
    required = ["host", "database", "user", "port"]
    missing = [k for k in required if not DB_CONFIG.get(k)]

    if missing:
        raise Exception(f"Missing DB config fields: {missing}")

    if DB_CONFIG.get("password") is None:
        DB_CONFIG["password"] = ""

    logger.info("✅ DB config ready")

except Exception as e:
    logger.error("❌ DB CONFIG ERROR: %s", str(e))
    raise