# =========================================================
# 📌 DATABASE CONFIG (POSTGRESQL READY)
# =========================================================
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # ✅ Parse Render PostgreSQL URL
    url = urlparse(DATABASE_URL)

    DB_CONFIG = {
        "host": url.hostname,
        "database": url.path[1:],   # remove leading '/'
        "user": url.username,
        "password": url.password,
        "port": url.port or 5432
    }

else:
    # ✅ Fallback (manual env variables)
    DB_CONFIG = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": int(os.getenv("DB_PORT", 5432))   # ✅ PostgreSQL default
    }


# =========================================================
# 📌 VALIDATION
# =========================================================
missing = [key for key, value in DB_CONFIG.items() if not value]

if missing:
    print(f"⚠️ Missing DB config: {missing}")
else:
    print("✅ PostgreSQL config loaded successfully")