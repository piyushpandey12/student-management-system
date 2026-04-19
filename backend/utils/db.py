# ================= IMPORTS =================
import psycopg2
import os
import logging
from psycopg2 import pool, OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor

# =========================================================
# 🔧 LOGGING SETUP
# =========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# 🔁 OPTIONAL LOCAL CONFIG
# =========================================================
try:
    from backend.config import DB_CONFIG
except ImportError:
    DB_CONFIG = None

# =========================================================
# 🔥 CONNECTION POOL
# =========================================================
connection_pool = None


def init_db_pool():
    global connection_pool

    if connection_pool:
        return

    try:
        # 🌐 PRODUCTION (Render / Railway / Neon)
        if os.getenv("PGHOST"):
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("PGHOST"),
                dbname=os.getenv("PGDATABASE"),
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                port=int(os.getenv("PGPORT", 5432)),
                sslmode="require"
            )

        # 🧪 CUSTOM ENV
        elif os.getenv("DB_HOST"):
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=int(os.getenv("DB_PORT", 5432)),
                sslmode="require"
            )

        # 🖥️ LOCAL CONFIG FILE
        elif DB_CONFIG:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DB_CONFIG["host"],
                dbname=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=int(DB_CONFIG.get("port", 5432)),
                sslmode="prefer"
            )

        else:
            raise Exception("No database configuration found")

        logger.info("✅ DB Pool Created")

    except Exception as e:
        logger.error("🔥 DB POOL ERROR: %s", str(e))
        raise


# =========================================================
# 📌 GET CONNECTION (SAFE + RETRY)
# =========================================================
def get_connection():
    global connection_pool

    if connection_pool is None:
        init_db_pool()

    try:
        conn = connection_pool.getconn()

        # 🔍 HEALTH CHECK
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (OperationalError, InterfaceError):
            logger.warning("⚠️ Stale connection detected, reconnecting...")
            connection_pool.putconn(conn, close=True)
            conn = connection_pool.getconn()

        return conn

    except Exception as e:
        logger.error("🔥 DB CONNECTION ERROR: %s", str(e))
        raise


# =========================================================
# 📌 GET CURSOR (DICT SUPPORT)
# =========================================================
def get_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)


# =========================================================
# 📌 RELEASE CONNECTION (SAFE)
# =========================================================
def release_connection(conn):
    global connection_pool

    try:
        if connection_pool and conn:
            connection_pool.putconn(conn)
    except Exception as e:
        logger.warning("⚠️ Release connection error: %s", str(e))


# =========================================================
# 📌 CLOSE POOL (CLEAN SHUTDOWN)
# =========================================================
def close_pool():
    global connection_pool

    try:
        if connection_pool:
            connection_pool.closeall()
            logger.info("🔒 DB Pool closed")
    except Exception as e:
        logger.warning("⚠️ Error closing pool: %s", str(e))