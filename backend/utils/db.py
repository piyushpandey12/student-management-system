import psycopg2
import os
from psycopg2 import pool

# Optional local config
try:
    from backend.config import DB_CONFIG
except ImportError:
    DB_CONFIG = None


# =========================================================
# 🔥 CONNECTION POOL (BEST PRACTICE)
# =========================================================
connection_pool = None


def init_db_pool():
    global connection_pool

    try:
        if os.getenv("PGHOST"):
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv("PGHOST"),
                dbname=os.getenv("PGDATABASE"),
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                port=int(os.getenv("PGPORT")),
                sslmode="require"
            )

        elif os.getenv("DB_HOST"):
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=int(os.getenv("DB_PORT", 5432)),
                sslmode="require"
            )

        elif DB_CONFIG:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=DB_CONFIG["host"],
                dbname=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=int(DB_CONFIG.get("port", 5432)),
                sslmode="prefer"   # ✅ FIXED for local
            )

        else:
            raise Exception("No database configuration found")

        print("✅ DB Pool Created")

    except Exception as e:
        print("🔥 DB POOL ERROR:", str(e))
        raise e


# =========================================================
# 📌 GET CONNECTION
# =========================================================
def get_connection():
    global connection_pool

    try:
        if connection_pool is None:
            init_db_pool()

        return connection_pool.getconn()

    except Exception as e:
        print("🔥 DB CONNECTION ERROR:", str(e))
        raise e   # ✅ IMPORTANT (don’t return None)


# =========================================================
# 📌 RELEASE CONNECTION
# =========================================================
def release_connection(conn):
    global connection_pool

    try:
        if connection_pool and conn:
            connection_pool.putconn(conn)
    except Exception as e:
        print("⚠️ Release connection error:", e)