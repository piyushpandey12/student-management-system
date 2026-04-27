from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# 🔐 SECRET KEY
# =========================================================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")


# =========================================================
# 🔐 GENERATE TOKEN (FIXED)
# =========================================================
def generate_token(identifier, role):
    payload = {
        "identifier": identifier,   # ✅ FIXED
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


# =========================================================
# 🔐 LOGIN REQUIRED
# =========================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token missing or invalid format"}), 401

        token = auth_header.split(" ")[1].strip()

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.user = decoded   # ✅ FIXED

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


# =========================================================
# 🔐 ROLE REQUIRED
# =========================================================
def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):

            user = getattr(g, "user", None)

            if not user:
                return jsonify({"error": "Unauthorized"}), 401

            if user.get("role") != required_role:
                return jsonify({"error": "Forbidden"}), 403

            return f(*args, **kwargs)

        return decorated
    return wrapper


# =========================================================
# 🔐 HASH PASSWORD
# =========================================================
def hash_password(password: str) -> str:
    password = (password or "").strip()

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    return generate_password_hash(password)


# =========================================================
# 🔐 VERIFY PASSWORD
# =========================================================
def verify_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password:
        return False

    return check_password_hash(
        stored_password,
        (provided_password or "").strip()
    )