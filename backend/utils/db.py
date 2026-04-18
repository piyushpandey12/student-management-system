import psycopg2
import os

# Optional local config (for development only)
try:
    from backend.config import DB_CONFIG
except ImportError:
    DB_CONFIG = None


def get_connection():
    try:
        # =========================================
        # 🔥 PRIORITY 1: RAILWAY / RENDER ENV
        # =========================================
        if os.getenv("PGHOST"):
            conn = psycopg2.connect(
                host=os.getenv("PGHOST"),
                dbname=os.getenv("PGDATABASE"),   # ✅ FIXED
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                port=int(os.getenv("PGPORT")),
                sslmode="require",
                connect_timeout=10
            )
            print("✅ PostgreSQL Connected (RAILWAY)")
            return conn

        # =========================================
        # 🔥 PRIORITY 2: GENERIC ENV (OPTIONAL)
        # =========================================
        elif os.getenv("DB_HOST"):
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),      # ✅ FIXED
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=int(os.getenv("DB_PORT", 5432)),
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
                dbname=DB_CONFIG["database"],     # ✅ FIXED
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=int(DB_CONFIG.get("port", 5432)),
                sslmode="require"
            )
            print("✅ PostgreSQL Connected (LOCAL)")
            return conn

        # =========================================
        # ❌ NO CONFIG FOUND
        # =========================================
        else:
            raise Exception("No database configuration found")

    except Exception as e:
        print("🔥 DB CONNECTION ERROR:", str(e))
        return None