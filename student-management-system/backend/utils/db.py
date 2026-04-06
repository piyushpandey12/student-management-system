import mysql.connector
from backend.config import DB_CONFIG

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
            ssl_disabled=False
        )

        if conn.is_connected():
            print("✅ DB CONNECTED")
            return conn
        else:
            print("❌ DB NOT CONNECTED")
            return None

    except Exception as e:
        print("🔥 DB ERROR:", e)
        return None