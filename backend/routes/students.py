# =========================================================
# 📌 IMPORTS
# =========================================================
from flask import Blueprint, request, jsonify, g
import logging

from backend.services.student_service import (
    get_all_students,
    create_student,
    remove_student,
    get_student_dashboard_data
)

from backend.utils.auth_utils import login_required, role_required

students_bp = Blueprint("students", __name__)
logger = logging.getLogger(__name__)


# =========================================================
# 📌 GET ALL STUDENTS
# =========================================================
@students_bp.route("/", methods=["GET"])
@login_required
@role_required("teacher")
def get_students():

    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(100, max(1, int(request.args.get("limit", 50))))
    except ValueError:
        return jsonify({"error": "Invalid pagination values"}), 400

    result, status = get_all_students(page, limit)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Failed to fetch students")
        }), status

    return jsonify({
        "status": "success",
        "data": result.get("data", []),
        "page": page,
        "limit": limit
    }), 200


# =========================================================
# 📌 ADD STUDENT (FINAL FIXED)
# =========================================================
@students_bp.route("/", methods=["POST"])
@login_required
@role_required("teacher")
def add_student():

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    rollno = (data.get("rollno") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # =========================================================
    # ✅ VALIDATION
    # =========================================================
    if not name or not rollno or not password:
        return jsonify({
            "status": "error",
            "message": "name, rollno, password required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "status": "error",
            "message": "Password must be at least 6 characters"
        }), 400

    try:
        result, status = create_student(rollno, name, password)

        if status >= 400:
            return jsonify({
                "status": "error",
                "message": result.get("error", "Failed to add student")
            }), status

        return jsonify({
            "status": "success",
            "message": result.get("message", "Student added successfully"),
            "rollno": rollno
        }), 201

    except Exception as e:
        logger.error(f"🔥 Add Student Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
@students_bp.route("/<rollno>", methods=["DELETE"])
@login_required
@role_required("teacher")
def delete_student(rollno):

    rollno = rollno.strip().lower()

    try:
        result, status = remove_student(rollno)

        if status >= 400:
            return jsonify({
                "status": "error",
                "message": result.get("error", "Failed to delete student")
            }), status

        return jsonify({
            "status": "success",
            "message": result.get("message", "Deleted successfully")
        }), 200

    except Exception as e:
        logger.error(f"🔥 Delete Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


# =========================================================
# 📌 STUDENT DASHBOARD
# =========================================================
@students_bp.route("/dashboard/<rollno>", methods=["GET"])
@login_required
def student_dashboard(rollno):

    rollno = rollno.strip().lower()

    # 🔐 ACCESS CONTROL
    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 403

    try:
        result, status = get_student_dashboard_data(rollno)

        if status >= 400:
            return jsonify({
                "status": "error",
                "message": result.get("error", "Failed to load dashboard")
            }), status

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"🔥 Dashboard Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500