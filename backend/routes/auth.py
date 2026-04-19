# ================= IMPORTS =================
from flask import Blueprint, request, jsonify

from backend.services.auth_service import (
    register_user,
    login_user,
    google_login_service
)

# ================= BLUEPRINT =================
auth_bp = Blueprint("auth", __name__)


# =========================================================
# 📌 REGISTER
# =========================================================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    identifier = (
        data.get("rollno") or
        data.get("teacherId") or
        data.get("identifier") or ""
    ).lower().strip()

    password = data.get("password")
    role = data.get("role", "student")
    name = data.get("name", "User")

    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "Identifier & password required"
        }), 400

    result, status = register_user(identifier, password, role, name)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Registration failed")
        }), status

    return jsonify({
        "status": "success",
        "message": result.get("message", "Registered successfully")
    }), status


# =========================================================
# 📌 LOGIN
# =========================================================
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    identifier = (
        data.get("rollno") or
        data.get("teacherId") or
        data.get("identifier") or ""
    ).lower().strip()

    password = data.get("password")

    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "Missing credentials"
        }), 400

    result, status = login_user(identifier, password)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Login failed")
        }), status

    return jsonify({
        "status": "success",
        "token": result["token"],
        "user": result["user"]
    }), 200


# =========================================================
# 🔐 GOOGLE LOGIN
# =========================================================
@auth_bp.route("/google", methods=["POST"])
def google_login():

    data = request.get_json() or {}
    token = data.get("token")

    if not token:
        return jsonify({
            "status": "error",
            "message": "Token missing"
        }), 400

    result, status = google_login_service(token)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Google login failed")
        }), status

    return jsonify({
        "status": "success",
        "token": result["token"],
        "user": result["user"]
    }), 200
