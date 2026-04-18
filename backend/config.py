# =========================================================
# 📌 DATABASE CONFIG (POSTGRESQL READY)
# =========================================================
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {}

if DATABASE_URL:
    try:
        # ✅ Parse DATABASE_URL (Render / Railway / Neon)
        url = urlparse(DATABASE_URL)

        DB_CONFIG = {
            "host": url.hostname,
            "database": url.path.lstrip("/"),   # safer than [1:]
            "user": url.username,
            "password": url.password,
            "port": url.port or 5432,
            "sslmode": "require"   # ✅ IMPORTANT for cloud DB
        }

        print("✅ Using DATABASE_URL config")

    except Exception as e:
        print("❌ Error parsing DATABASE_URL:", e)


else:
    # =========================================================
    # 📌 FALLBACK (LOCAL DEV)
    # =========================================================
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "student_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "sslmode": "prefer"   # local doesn't need require
    }

    print("⚠️ Using LOCAL DB config")


# =========================================================
# 📌 VALIDATION
# =========================================================
required_keys = ["host", "database", "user", "password", "port"]

missing = [key for key in required_keys if not DB_CONFIG.get(key)]

if missing:
    raise Exception(f"🔥 Missing DB config: {missing}")
else:
    print("✅ PostgreSQL config loaded successfully")