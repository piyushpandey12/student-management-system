# ================= IMPORTS =================
from flask import Blueprint, request, jsonify, g

from backend.services.student_service import (
    get_all_students,
    create_student,
    remove_student,
    get_student_dashboard_data
)

from backend.utils.auth_utils import hash_password
from backend.utils.auth_utils import login_required, role_required

# ================= BLUEPRINT =================
students_bp = Blueprint("students", __name__)


# =========================================================
# 📌 GET ALL STUDENTS (SECURE)
# =========================================================
@students_bp.route("/", methods=["GET"])
@login_required
@role_required("teacher")
def get_students():

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid pagination values"
        }), 400

    result, status = get_all_students(page, limit)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Failed to fetch students")
        }), status

    return jsonify({
        "status": "success",
        "data": result["data"],
        "page": result["page"],
        "limit": result["limit"]
    }), 200


# =========================================================
# 📌 ADD STUDENT (SECURE)
# =========================================================
@students_bp.route("/", methods=["POST"])
@login_required
@role_required("teacher")
def add_student():

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    rollno = (data.get("rollno") or "").strip().lower()

    if not name or not rollno:
        return jsonify({
            "status": "error",
            "message": "Name & RollNo required"
        }), 400

    password_hash = hash_password("default123")

    result, status = create_student(rollno, name, password_hash)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Failed to add student")
        }), status

    return jsonify({
        "status": "success",
        "message": result.get("message", "Student added successfully"),
        "rollno": rollno
    }), status


# =========================================================
# 📌 DELETE STUDENT (SECURE)
# =========================================================
@students_bp.route("/<rollno>", methods=["DELETE"])
@login_required
@role_required("teacher")
def delete_student(rollno):

    rollno = rollno.strip().lower()

    result, status = remove_student(rollno)

    if status >= 400:
        return jsonify({
            "status": "error",
            "message": result.get("error", "Failed to delete student")
        }), status

    return jsonify({
        "status": "success",
        "message": result.get("message", "Deleted successfully")
    }), status


# =========================================================
# 📌 STUDENT DASHBOARD (SECURE + ANALYSIS)
# =========================================================
@students_bp.route("/dashboard/<rollno>", methods=["GET"])
@login_required
def student_dashboard(rollno):

    rollno = rollno.strip().lower()

    # 🔐 Student can only access own data
    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 403

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
