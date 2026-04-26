# ================= IMPORTS =================
from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# 🔐 SECRET KEY (JWT) — SINGLE SOURCE OF TRUTH
# =========================================================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")


# =========================================================
# 🔐 TOKEN GENERATION (FIXED)
# =========================================================
def generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # PyJWT >=2 returns str, older returns bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


# =========================================================
# 🔐 LOGIN REQUIRED DECORATOR
# =========================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            # Remove "Bearer "
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


# =========================================================
# 🔐 ROLE REQUIRED DECORATOR
# =========================================================
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, "user", None)

            if not user:
                return jsonify({"error": "Unauthorized"}), 401

            if user.get("role") != role:
                return jsonify({"error": "Forbidden"}), 403

            return f(*args, **kwargs)

        return decorated
    return wrapper


# =========================================================
# 🔐 HASH PASSWORD
# =========================================================
def hash_password(password: str) -> str:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty")

    password = password.strip()

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    return generate_password_hash(
        password,
        method="pbkdf2:sha256",
        salt_length=16
    )


# =========================================================
# 🔐 VERIFY PASSWORD
# =========================================================
def verify_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password:
        return False

    if not provided_password or not provided_password.strip():
        return False

    try:
        return check_password_hash(
            stored_password,
            provided_password.strip()
        )
    except Exception:
        return False


# =========================================================
# 🔐 GOOGLE USER CHECK
# =========================================================
def is_google_user(stored_password: str) -> bool:
    return not stored_password


# =========================================================
# 🔐 VALIDATE PASSWORD
# =========================================================
def validate_password(password: str) -> tuple:
    if not password or not password.strip():
        return False, "Password cannot be empty"

    password = password.strip()

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if password.isdigit():
        return False, "Password cannot be only numbers"

    if not any(c.isalpha() for c in password):
        return False, "Password must include letters"

    return True, "Valid password"