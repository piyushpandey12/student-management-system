# ================= IMPORTS =================
import os
import jwt
from datetime import datetime, timedelta

from backend.utils.db import get_connection, get_cursor, release_connection
from backend.utils.auth_utils import hash_password, verify_password

# ================= CONFIG =================
SECRET_KEY = os.getenv("SECRET_KEY", "student-secret")


# =========================================================
# 🔐 GENERATE TOKEN
# =========================================================
def generate_token(identifier, role):
    payload = {
        "identifier": identifier,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# =========================================================
# 📌 REGISTER USER
# =========================================================
def register_user(identifier, name, password, role):
    conn = None

    try:
        identifier = identifier.lower().strip()

        conn = get_connection()
        cur = get_cursor(conn)  # ✅ dict cursor

        # 🔍 check existing user
        cur.execute("SELECT id FROM users WHERE identifier=%s", (identifier,))
        if cur.fetchone():
            return {"error": "User already exists"}

        # 🔐 hash password
        hashed = hash_password(password)

        # 📥 insert user
        cur.execute("""
            INSERT INTO users (identifier, name, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (identifier, name, hashed, role))

        user = cur.fetchone()
        user_id = user["id"]

        # 👇 insert into role-specific table
        if role == "student":
            cur.execute("""
                INSERT INTO students (rollno, name, user_id)
                VALUES (%s, %s, %s)
            """, (identifier, name, user_id))

        elif role == "teacher":
            cur.execute("""
                INSERT INTO teachers (teacher_id, name, user_id)
                VALUES (%s, %s, %s)
            """, (identifier, name, user_id))

        conn.commit()

        return {"success": True}

    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}

    finally:
        if conn:
            release_connection(conn)


# =========================================================
# 📌 LOGIN USER
# =========================================================
def login_user(identifier, password):
    conn = None

    try:
        identifier = identifier.lower().strip()

        conn = get_connection()
        cur = get_cursor(conn)  # ✅ dict cursor

        cur.execute("""
            SELECT identifier, password, role
            FROM users
            WHERE identifier=%s
        """, (identifier,))

        user = cur.fetchone()

        if not user:
            return {"error": "User not found"}

        # 🔐 verify hashed password
        if not verify_password(user["password"], password):
            return {"error": "Invalid credentials"}

        # 🔑 generate token
        token = generate_token(user["identifier"], user["role"])

        return {
            "token": token,
            "user": {
                "identifier": user["identifier"],
                "role": user["role"]
            }
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if conn:
            release_connection(conn)