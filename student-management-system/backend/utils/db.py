import mysql.connector
import os

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT"))
        )
        return conn
    except Exception as e:
        print("DB ERROR:", e)
        return None


# 🔥 ADD THIS (IMPORTANT FIX)
def get_db_connection():
    return get_connection()