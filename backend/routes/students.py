# ================= IMPORTS =================
from flask import Blueprint, request, jsonify, g

from backend.services.student_service import (
    get_all_students,
    create_student,
    remove_student,
    get_student_dashboard_data
)

from backend.utils.auth_utils import login_required, role_required

students_bp = Blueprint("students", __name__)


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
        return jsonify({"error": result.get("error", "Failed to fetch students")}), status

    return jsonify({
        "status": "success",
        "data": result["data"],
        "page": page,
        "limit": limit
    }), 200


# =========================================================
# 📌 ADD STUDENT
# =========================================================
@students_bp.route("/", methods=["POST"])
@login_required
@role_required("teacher")
def add_student():

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    rollno = (data.get("rollno") or "").strip().lower()
    password = data.get("password")  # 🔥 now dynamic

    if not name or not rollno or not password:
        return jsonify({"error": "name, rollno, password required"}), 400

    # 🔒 basic validation
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    result, status = create_student(rollno, name, password)

    if status >= 400:
        return jsonify({"error": result.get("error", "Failed to add student")}), status

    return jsonify({
        "status": "success",
        "message": result.get("message", "Student added successfully"),
        "rollno": rollno
    }), status


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
@students_bp.route("/<rollno>", methods=["DELETE"])
@login_required
@role_required("teacher")
def delete_student(rollno):

    rollno = rollno.strip().lower()

    result, status = remove_student(rollno)

    if status >= 400:
        return jsonify({"error": result.get("error", "Failed to delete student")}), status

    return jsonify({
        "status": "success",
        "message": result.get("message", "Deleted successfully")
    }), status


# =========================================================
# 📌 STUDENT DASHBOARD
# =========================================================
@students_bp.route("/dashboard/<rollno>", methods=["GET"])
@login_required
def student_dashboard(rollno):

    rollno = rollno.strip().lower()

    # 🔐 Access control
    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({"error": "Unauthorized"}), 403

    result, status = get_student_dashboard_data(rollno)

    if status >= 400:
        return jsonify({"error": result.get("error", "Failed to load dashboard")}), status

    return jsonify({
        "status": "success",
        "data": result
    }), 200