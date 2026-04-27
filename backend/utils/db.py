# ================= IMPORTS =================
import psycopg2
import logging
from psycopg2 import pool, OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor

from backend.config import DB_CONFIG   # ✅ SINGLE SOURCE OF TRUTH

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= GLOBAL POOL =================
connection_pool = None


# =========================================================
# 🔥 INIT DB POOL (UNIFIED)
# =========================================================
def init_db_pool():
    global connection_pool

    if connection_pool:
        return

    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=DB_CONFIG["host"],
            dbname=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
            sslmode=DB_CONFIG["sslmode"]
        )

        logger.info(f"✅ DB Pool Created → {DB_CONFIG['host']}")

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

        # 🔒 Ensure clean transaction state
        conn.autocommit = False

        # 🔍 Health check
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (OperationalError, InterfaceError):
            logger.warning("⚠️ Stale connection detected → reconnecting")
            connection_pool.putconn(conn, close=True)
            conn = connection_pool.getconn()

        return conn

    except Exception as e:
        logger.error("🔥 DB CONNECTION ERROR: %s", str(e))
        raise


# =========================================================
# 📌 GET CURSOR (DICT FORMAT)
# =========================================================
def get_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)


# =========================================================
# 📌 RELEASE CONNECTION (SAFE RESET)
# =========================================================
def release_connection(conn):
    global connection_pool

    try:
        if conn:
            conn.rollback()  # 🔒 reset transaction
            connection_pool.putconn(conn)

    except Exception as e:
        logger.warning("⚠️ Release connection error: %s", str(e))


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