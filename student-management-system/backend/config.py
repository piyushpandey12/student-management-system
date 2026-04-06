# =========================================================
# 📌 DATABASE CONFIG (UNIFIED - PRODUCTION READY)
# =========================================================
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST") or os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST"),
    "user": os.getenv("DB_USER") or os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER"),
    "password": os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DB"),
    "port": int(os.getenv("DB_PORT") or os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT", 3306))
}


# =========================================================
# 📌 VALIDATION (SAFE)
# =========================================================
missing = [key for key, value in DB_CONFIG.items() if value is None]

if missing:
    print(f"⚠️ Warning: Missing DB environment variables: {missing}")