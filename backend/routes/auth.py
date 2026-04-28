# ================= IMPORTS =================
from flask import Blueprint, request, jsonify
from backend.services.auth_service import register_user, login_user

# ================= BLUEPRINT =================
auth_bp = Blueprint("auth", __name__)


# =========================================================
# 📌 HELPER: EXTRACT IDENTIFIER
# =========================================================
def extract_identifier(data):
    return (
        data.get("rollno") or
        data.get("teacherId") or
        data.get("identifier") or ""
    ).strip().lower()


# =========================================================
# 📌 REGISTER
# =========================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(silent=True) or {}

        identifier = extract_identifier(data)
        password = (data.get("password") or "").strip()
        role = data.get("role", "student")
        name = data.get("name", "User")

        # ✅ Validation
        if not identifier or not password:
            return jsonify({
                "status": "error",
                "message": "Identifier & password required"
            }), 400

        if len(password) < 4:
            return jsonify({
                "status": "error",
                "message": "Password must be at least 4 characters"
            }), 400

        result = register_user(identifier, name, password, role)

        if result.get("error"):
            return jsonify({
                "status": "error",
                "message": result["error"]
            }), 400

        return jsonify({
            "status": "success",
            "message": "User registered successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================================================
# 📌 LOGIN
# =========================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        identifier = extract_identifier(data)
        password = (data.get("password") or "").strip()

        # ✅ Validation
        if not identifier or not password:
            return jsonify({
                "status": "error",
                "message": "Missing credentials"
            }), 400

        result = login_user(identifier, password)

        if result.get("error"):
            return jsonify({
                "status": "error",
                "message": result["error"]
            }), 401

        return jsonify({
            "status": "success",
            "token": result["token"],
            "user": result["user"]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500