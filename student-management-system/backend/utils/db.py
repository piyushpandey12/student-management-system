import mysql.connector
from config import DB_CONFIG


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
            connection_timeout=10
        )

        if conn.is_connected():
            return conn

        return None

    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None


# Backward compatibility
def get_db_connection():
    return get_connection()