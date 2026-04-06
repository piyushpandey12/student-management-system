import mysql.connector


def get_connection():
    try:
        conn = mysql.connector.connect(
            host="centerbeam.proxy.rlwy.net",   
            user="root",                       
            password="gpNYiPlqWaeXxYcsqssdwgSeDPWshwR",  
            database="railway",               
            port=55552                         
        )

        print("✅ DB Connected Successfully")
        return conn

    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None


# Optional (for compatibility)
def get_db_connection():
    return get_connection()