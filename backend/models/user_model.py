# auth_model.py

import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import RealDictCursor


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
# ✅ REGISTER USER (LOCAL ONLY)
# =========================================
def register_user(identifier, name, password, role):
    conn = get_connection()
    cur = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cur.execute("""
            INSERT INTO users (identifier, name, password, role)
            VALUES (%s, %s, %s, %s)
        """, (identifier, name, hashed_password, role))

        conn.commit()
        return {"success": True}

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"error": "User already exists"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ GET USER
# =========================================
def get_user(identifier):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, identifier, password, role
        FROM users
        WHERE identifier=%s
    """, (identifier,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user  # already dict


# =========================================
# ✅ LOGIN USER (LOCAL)
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
            "id": user["id"],
            "identifier": user["identifier"],
            "role": user["role"]
        }
    }


# =========================================
# ✅ DELETE USER
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