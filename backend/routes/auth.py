# ================= IMPORTS =================
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from backend.services.auth_service import register_user, login_user
from backend.utils.db import get_connection, release_connection

# ================= BLUEPRINT =================
auth_bp = Blueprint("auth", __name__)


# =========================================================
# 📌 HELPER: EXTRACT IDENTIFIER (UNIFIED SYSTEM)
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

        if not identifier or not password:
            return jsonify({"status": "error", "message": "Identifier & password required"}), 400

        if len(password) < 4:
            return jsonify({"status": "error", "message": "Password must be at least 4 characters"}), 400

        # 🔐 ALWAYS HASH
        hashed_password = generate_password_hash(password)

        result = register_user(identifier, name, hashed_password, role)

        if result.get("error"):
            return jsonify({"status": "error", "message": result["error"]}), 400

        return jsonify({"status": "success", "message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# =========================================================
# 📌 LOGIN
# =========================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        identifier = extract_identifier(data)
        password = (data.get("password") or "").strip()

        if not identifier or not password:
            return jsonify({"status": "error", "message": "Missing credentials"}), 400

        # ⚠️ Ensure your auth_service uses check_password_hash internally
        result = login_user(identifier, password)

        if result.get("error"):
            return jsonify({"status": "error", "message": result["error"]}), 401

        return jsonify({
            "status": "success",
            "token": result["token"],
            "user": result["user"]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# =========================================================
# 📌 RESET PASSWORD (FINAL FIXED VERSION)
# =========================================================
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    conn = None
    cursor = None

    try:
        data = request.get_json(silent=True) or {}

        identifier = extract_identifier(data)
        new_password = (data.get("newPassword") or "").strip()

        if not identifier or not new_password:
            return jsonify({
                "status": "error",
                "message": "Identifier & new password required"
            }), 400

        if len(new_password) < 4:
            return jsonify({
                "status": "error",
                "message": "Password must be at least 4 characters"
            }), 400

        # 🔐 HASH PASSWORD (CRITICAL FIX)
        hashed_password = generate_password_hash(new_password)

        conn = get_connection()
        cursor = conn.cursor()

        # 🔍 Check teacher first
        cursor.execute("SELECT 1 FROM teachers WHERE teacher_id=%s", (identifier,))
        user = cursor.fetchone()

        table = None
        column = None

        if user:
            table = "teachers"
            column = "teacher_id"
        else:
            cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (identifier,))
            user = cursor.fetchone()
            if user:
                table = "students"
                column = "rollno"

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        # 🔐 UPDATE
        cursor.execute(
            f"UPDATE {table} SET password=%s WHERE {column}=%s",
            (hashed_password, identifier)
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Password reset successful"
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        print("RESET ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server error"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)