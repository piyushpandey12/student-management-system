# auth_guard.py

from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from datetime import datetime, timezone

# 🔐 Secret key (must match token generation)
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "a3db328b39032b567c22bc38eab2c96db301f4450ee47859d5d887ebf308ca88"
)

ALGORITHM = "HS256"


# =========================================
# ✅ VERIFY TOKEN FUNCTION
# =========================================
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 🔒 Optional: manual expiration check (extra safety)
        if "exp" in payload:
            if datetime.fromtimestamp(payload["exp"], timezone.utc) < datetime.now(timezone.utc):
                return {"error": "Token expired"}

        return payload

    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}

    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


# =========================================
# ✅ LOGIN REQUIRED DECORATOR
# =========================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        # 🔴 Strict validation
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Authorization header must be 'Bearer <token>'"
            }), 401

        # Extract token safely
        token = auth_header.split(" ")[1].strip()

        if not token:
            return jsonify({"error": "Token missing"}), 401

        user = verify_token(token)

        if "error" in user:
            return jsonify(user), 401

        # Attach user to request context
        g.user = user

        return f(*args, **kwargs)

    return decorated


# =========================================
# ✅ ROLE BASED ACCESS
# =========================================
def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):

            user = getattr(g, "user", None)

            if not user:
                return jsonify({"error": "Unauthorized"}), 401

            if user.get("role") != required_role:
                return jsonify({
                    "error": "Forbidden: Access denied"
                }), 403

            return f(*args, **kwargs)

        return decorated
    return wrapper