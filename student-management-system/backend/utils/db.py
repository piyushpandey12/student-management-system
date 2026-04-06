import mysql.connector
import os

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306)),
            autocommit=False,
            connection_timeout=10   # ✅ prevents hanging
        )

        if conn.is_connected():
            return conn
        else:
            print("DB ERROR: Not connected")
            return None

    except mysql.connector.Error as e:
        print("DB ERROR:", e)
        return None

    except Exception as e:
        print("UNKNOWN ERROR:", e)
        return None