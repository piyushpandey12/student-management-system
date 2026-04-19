# user_model.py

import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================
# 🔌 DATABASE CONNECTION
# =========================================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "student_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password")
    )


# =========================================
# ✅ REGISTER USER (STUDENT / TEACHER)
# =========================================
def register_user(identifier, name, password, role):
    conn = get_connection()
    cur = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        if role == "student":
            cur.execute(
                "SELECT add_student(%s, %s, %s)",
                (identifier, name, hashed_password)
            )
        elif role == "teacher":
            cur.execute(
                "SELECT add_teacher(%s, %s, %s)",
                (identifier, name, hashed_password)
            )
        else:
            return {"error": "Invalid role"}

        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ GET USER BY IDENTIFIER
# =========================================
def get_user(identifier):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, identifier, password, role FROM users WHERE identifier=%s",
        (identifier,)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return None

    return {
        "id": user[0],
        "identifier": user[1],
        "password": user[2],
        "role": user[3]
    }


# =========================================
# ✅ LOGIN USER
# =========================================
def login_user(identifier, password):
    user = get_user(identifier)

    if not user:
        return {"error": "User not found"}

    if not check_password_hash(user["password"], password):
        return {"error": "Invalid password"}

    return {
        "success": True,
        "user": {
            "identifier": user["identifier"],
            "role": user["role"]
        }
    }


# =========================================
# ✅ DELETE USER (OPTIONAL)
# =========================================
def delete_user(identifier):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE identifier=%s", (identifier,))
        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()