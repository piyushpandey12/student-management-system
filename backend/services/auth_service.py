import os
import jwt
from datetime import datetime, timedelta
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import hash_password, verify_password

SECRET_KEY = os.getenv("SECRET_KEY", "student-secret")


def generate_token(identifier, role):
    payload = {
        "identifier": identifier,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def register_user(identifier, password, role, name):
    identifier = identifier.lower().strip()

    db = get_connection()
    cur = db.cursor()

    try:
        cur.execute("SELECT 1 FROM users WHERE identifier=%s", (identifier,))
        if cur.fetchone():
            return {"error": "User already exists"}, 409

        hashed = hash_password(password)

        cur.execute("""
            INSERT INTO users (identifier, name, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (identifier, name, hashed, role))

        user_id = cur.fetchone()[0]

        if role == "student":
            cur.execute("""
                INSERT INTO students (rollno, name, user_id)
                VALUES (%s, %s, %s)
            """, (identifier, name, user_id))
        else:
            cur.execute("""
                INSERT INTO teachers (teacher_id, name, user_id)
                VALUES (%s, %s, %s)
            """, (identifier, name, user_id))

        db.commit()
        return {"message": "Registered"}, 201

    except Exception:
        db.rollback()
        return {"error": "Registration failed"}, 500

    finally:
        cur.close()
        release_connection(db)


def login_user(identifier, password):
    identifier = identifier.lower().strip()

    db = get_connection()
    cur = db.cursor()

    try:
        cur.execute("""
            SELECT password, role
            FROM users
            WHERE identifier=%s
        """, (identifier,))

        user = cur.fetchone()

        if not user:
            return {"error": "User not found"}, 404

        db_password, role = user

        if not verify_password(db_password, password):
            return {"error": "Invalid credentials"}, 401

        token = generate_token(identifier, role)

        return {
            "token": token,
            "user": {
                "identifier": identifier,
                "role": role
            }
        }, 200

    except Exception:
        return {"error": "Login failed"}, 500

    finally:
        cur.close()
        release_connection(db)