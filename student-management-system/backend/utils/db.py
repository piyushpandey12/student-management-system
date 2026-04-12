import psycopg2
import os

# Optional local config
try:
    from backend.config import DB_CONFIG
except ImportError:
    DB_CONFIG = None


def get_connection():
    try:
        # =========================================
        # 🔥 PRIORITY 1: RAILWAY / POSTGRES ENV
        # =========================================
        if os.getenv("PGHOST"):
            conn = psycopg2.connect(
                host=os.getenv("PGHOST"),
                database=os.getenv("PGDATABASE"),
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                port=os.getenv("PGPORT", 5432),
                sslmode="require"
            )
            print("✅ PostgreSQL Connected (RAILWAY)")
            return conn

        # =========================================
        # 🔥 PRIORITY 2: GENERIC ENV (OPTIONAL)
        # =========================================
        elif os.getenv("DB_HOST"):
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=os.getenv("DB_PORT", 5432),
                sslmode="require"
            )
            print("✅ PostgreSQL Connected (ENV)")
            return conn

        # =========================================
        # 🏠 PRIORITY 3: LOCAL CONFIG (DEV)
        # =========================================
        elif DB_CONFIG:
            conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=DB_CONFIG.get("port", 5432),
                sslmode="require"
            )
            print("✅ PostgreSQL Connected (LOCAL CONFIG)")
            return conn

        # =========================================
        # ❌ NO CONFIG FOUND
        # =========================================
        else:
            raise Exception("No database configuration found")

    except Exception as e:
        print("🔥 DB CONNECTION ERROR:", e)
        return None