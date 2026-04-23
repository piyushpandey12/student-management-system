# ================= IMPORTS =================
import os
import jwt
from datetime import datetime, timedelta

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import hash_password, verify_password

# ================= SECRET =================
SECRET_KEY = os.getenv("SECRET_KEY", "student-management-secret")


# =========================================================
# 🔑 GENERATE JWT TOKEN (FIXED)
# =========================================================
def generate_token(identifier, role):
    payload = {
        "identifier": identifier,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=6)  # increased expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# =========================================================
# 📌 REGISTER USER
# =========================================================
def register_user(identifier, password, role, name="User"):
    identifier = identifier.lower().strip()

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT 1 FROM users WHERE identifier=%s", (identifier,))
        if cursor.fetchone():
            return {"error": "User already exists"}, 409

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users (identifier, password, role)
            VALUES (%s, %s, %s)
        """, (identifier, hashed_password, role))

        if role == "student":
            cursor.execute("""
                INSERT INTO students (rollno, name)
                VALUES (%s, %s)
            """, (identifier, name))
        else:
            cursor.execute("""
                INSERT INTO teachers (teacher_id, name)
                VALUES (%s, %s)
            """, (identifier, name))

        db.commit()

        return {"message": "Registered successfully"}, 201

    except Exception as e:
        if db:
            db.rollback()
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 📌 LOGIN USER
# =========================================================
def login_user(identifier, password):
    identifier = identifier.lower().strip()

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT password, role
            FROM users
            WHERE identifier=%s
        """, (identifier,))

        user = cursor.fetchone()

        if not user:
            return {"error": "User not found"}, 404

        db_password, role = user

        if not db_password or not verify_password(db_password, password):
            return {"error": "Invalid credentials"}, 401

        token = generate_token(identifier, role)

        return {
            "token": token,
            "user": {
                "id": identifier,
                "role": role
            }
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 🔐 GOOGLE SIGNUP (FIXED)
# =========================================================
def google_signup_service(token, role="student"):
    db = None
    cursor = None

    try:
        # ✅ VERIFY GOOGLE TOKEN (CORRECT METHOD)
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request()
        )

        email = idinfo.get("email", "").lower()
        name = idinfo.get("name", "User")

        if not email:
            return {"error": "Invalid Google token"}, 401

        db = get_connection()
        cursor = db.cursor()

        # 🔎 CHECK USER
        cursor.execute("SELECT role FROM users WHERE identifier=%s", (email,))
        user = cursor.fetchone()

        if not user:
            # ✅ CREATE USER
            cursor.execute("""
                INSERT INTO users (identifier, password, role)
                VALUES (%s, %s, %s)
            """, (email, "", role))

            if role == "student":
                cursor.execute("""
                    INSERT INTO students (rollno, name)
                    VALUES (%s, %s)
                """, (email, name))
            else:
                cursor.execute("""
                    INSERT INTO teachers (teacher_id, name)
                    VALUES (%s, %s)
                """, (email, name))

            db.commit()
        else:
            role = user[0]

        jwt_token = generate_token(email, role)

        return {
            "token": jwt_token,
            "user": {
                "id": email,
                "role": role
            }
        }, 200

    except Exception as e:
        if db:
            db.rollback()
        return {"error": str(e)}, 401

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 🔐 GOOGLE LOGIN (OPTIONAL CLEAN)
# =========================================================
def google_login_service(token):
    # Just reuse signup logic
    return google_signup_service(token)