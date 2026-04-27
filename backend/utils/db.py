# ================= IMPORTS =================
import os
import logging
import psycopg2
from psycopg2 import pool, OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

# Optional fallback (local only)
try:
    from backend.config import DB_CONFIG
except:
    DB_CONFIG = None

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= GLOBAL POOL =================
connection_pool = None


# =========================================================
# 🔥 INIT DB POOL (PRODUCTION + LOCAL SAFE)
# =========================================================
def init_db_pool():
    global connection_pool

    if connection_pool:
        return

    try:
        database_url = os.getenv("DATABASE_URL")

        # ================= PRODUCTION (Render) =================
        if database_url:
            result = urlparse(database_url)

            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port,
                database=result.path[1:],
                sslmode="require"
            )

            logger.info("✅ Connected to Render PostgreSQL")

        # ================= LOCAL FALLBACK =================
        elif DB_CONFIG:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DB_CONFIG["host"],
                dbname=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=DB_CONFIG["port"],
                sslmode=DB_CONFIG.get("sslmode", "prefer")
            )

            logger.warning("⚠️ Using LOCAL DB config")

        else:
            raise Exception("❌ No database configuration found")

    except Exception as e:
        logger.error("🔥 DB POOL ERROR: %s", str(e))
        raise


# =========================================================
# 📌 GET CONNECTION (SAFE + HEALTH CHECK)
# =========================================================
def get_connection():
    global connection_pool

    if connection_pool is None:
        init_db_pool()

    try:
        conn = connection_pool.getconn()

        conn.autocommit = False

        # 🔍 Health check
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (OperationalError, InterfaceError):
            logger.warning("⚠️ Stale connection → reconnecting")
            connection_pool.putconn(conn, close=True)
            conn = connection_pool.getconn()

        return conn

    except Exception as e:
        logger.error("🔥 DB CONNECTION ERROR: %s", str(e))
        raise


# =========================================================
# 📌 GET CURSOR (DICT)
# =========================================================
def get_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)


# =========================================================
# 📌 RELEASE CONNECTION
# =========================================================
def release_connection(conn):
    global connection_pool

    try:
        if conn:
            conn.rollback()
            connection_pool.putconn(conn)

    except Exception as e:
        logger.warning("⚠️ Release error: %s", str(e))


# =========================================================
# 📌 CLOSE POOL
# =========================================================
def close_pool():
    global connection_pool

    try:
        if connection_pool:
            connection_pool.closeall()
            logger.info("🔒 DB Pool closed")

    except Exception as e:
        logger.warning("⚠️ Close pool error: %s", str(e))