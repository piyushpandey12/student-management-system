# auth_guard.py

from functools import wraps
from flask import request, jsonify, g
import jwt
import os

# 🔐 Secret key (keep same as your main app)
SECRET_KEY = os.getenv("SECRET_KEY", "a3db328b39032b567c22bc38eab2c96db301f4450ee47859d5d887ebf308ca88")


# =========================================
# ✅ VERIFY TOKEN FUNCTION
# =========================================
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
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
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        try:
            token = auth_header.split(" ")[1]
        except:
            return jsonify({"error": "Invalid token format"}), 401

        user = verify_token(token)

        if "error" in user:
            return jsonify(user), 401

        # attach user globally
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

            if not hasattr(g, "user"):
                return jsonify({"error": "Unauthorized"}), 401

            if g.user.get("role") != required_role:
                return jsonify({"error": "Forbidden: Access denied"}), 403

            return f(*args, **kwargs)

        return decorated
    return wrapper
