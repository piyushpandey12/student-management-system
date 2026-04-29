# ================= IMPORTS =================
import os
import jwt
from datetime import datetime, timedelta

from backend.utils.db import get_connection, get_cursor, release_connection
from werkzeug.security import generate_password_hash, check_password_hash

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
        identifier = (identifier or "").strip().lower()
        name = (name or "").strip()
        password = (password or "").strip()

        if not identifier or not name or not password:
            return {"error": "All fields required"}

        conn = get_connection()
        cur = get_cursor(conn)

        # 🔍 CHECK EXISTING
        cur.execute("SELECT id FROM users WHERE identifier=%s", (identifier,))
        if cur.fetchone():
            return {"error": "User already exists"}

        # 🔐 HASH PASSWORD
        hashed = generate_password_hash(password)

        # 📥 INSERT USER
        cur.execute("""
            INSERT INTO users (identifier, name, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (identifier, name, hashed, role))

        user_id = cur.fetchone()["id"]

        # 👇 ROLE TABLE INSERT
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
        print("REGISTER ERROR:", e)
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
        identifier = (identifier or "").strip().lower()
        password = (password or "").strip()

        if not identifier or not password:
            return {"error": "Missing credentials"}

        conn = get_connection()
        cur = get_cursor(conn)

        cur.execute("""
            SELECT id, identifier, password, role, name
            FROM users
            WHERE identifier=%s
        """, (identifier,))

        user = cur.fetchone()

        if not user:
            return {"error": "User not found"}

        # 🔍 DEBUG (remove after testing)
        print("INPUT:", password)
        print("HASH:", user["password"])
        print("MATCH:", check_password_hash(user["password"], password))

        # 🔐 VERIFY PASSWORD
        if not check_password_hash(user["password"], password):
            return {"error": "Invalid password"}

        # 🔑 TOKEN
        token = generate_token(user["identifier"], user["role"])

        return {
            "token": token,
            "user": {
                "id": user["id"],
                "identifier": user["identifier"],
                "name": user["name"],
                "role": user["role"]
            }
        }

    except Exception as e:
        print("LOGIN ERROR:", e)
        return {"error": str(e)}

    finally:
        if conn:
            release_connection(conn)


# =========================================================
# ❌ DELETE USER (FULL CLEAN DELETE)
# =========================================================
def delete_user(identifier):
    conn = None

    try:
        identifier = (identifier or "").strip().lower()

        conn = get_connection()
        cur = get_cursor(conn)

        # 🔍 GET USER
        cur.execute("""
            SELECT id, role FROM users WHERE identifier=%s
        """, (identifier,))
        user = cur.fetchone()

        if not user:
            return {"error": "User not found"}

        user_id = user["id"]
        role = user["role"]

        # 🔥 DELETE CHILD TABLE FIRST
        if role == "student":
            cur.execute("DELETE FROM students WHERE user_id=%s", (user_id,))
        elif role == "teacher":
            cur.execute("DELETE FROM teachers WHERE user_id=%s", (user_id,))

        # 🔥 DELETE MAIN USER
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))

        conn.commit()
        return {"success": True}

    except Exception as e:
        if conn:
            conn.rollback()
        print("DELETE ERROR:", e)
        return {"error": str(e)}

    finally:
        if conn:
            release_connection(conn)