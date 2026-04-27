# =========================================================
# 📌 IMPORTS
# =========================================================
from flask import Blueprint, jsonify, request, g
from backend.utils.db import get_connection, release_connection
from datetime import datetime
from psycopg2.extras import RealDictCursor
from backend.utils.auth_utils import login_required, role_required
import logging

attendance_bp = Blueprint('attendance', __name__)
logger = logging.getLogger(__name__)


# =========================================================
# 📌 MARK ATTENDANCE (FIXED)
# =========================================================
@attendance_bp.route("/mark", methods=["POST"])
@login_required
@role_required("teacher")
def mark_attendance():

    data = request.get_json(silent=True) or {}

    rollno = (data.get("rollno") or "").strip().lower()
    date = data.get("date")
    status = (data.get("status") or "").strip().lower()

    teacher_id = g.user.get("identifier")

    # ✅ VALIDATION
    if not rollno or not date or not status:
        return jsonify({"error": "rollno, date, status required"}), 400

    if status not in ["present", "absent"]:
        return jsonify({"error": "Invalid status"}), 400

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format (YYYY-MM-DD)"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 🔒 CHECK STUDENT EXISTS
        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        # ✅ UPSERT ATTENDANCE
        cursor.execute(
            "SELECT mark_attendance(%s, %s, %s, %s)",
            (rollno, date, status, teacher_id)
        )

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Attendance marked successfully"
        }), 200

    except Exception as e:
        if db:
            db.rollback()

        logger.error(f"🔥 Attendance Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)   # ✅ show real error
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 📌 GET ATTENDANCE
# =========================================================
@attendance_bp.route("/<rollno>", methods=["GET"])
@login_required
def get_attendance(rollno):

    rollno = rollno.strip().lower()

    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({"error": "Unauthorized"}), 403

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT date, status
            FROM attendance
            WHERE rollno = %s
            ORDER BY date DESC
        """, (rollno,))

        rows = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": [
                {
                    "date": r["date"].strftime("%Y-%m-%d"),
                    "status": r["status"]
                }
                for r in rows
            ]
        }), 200

    except Exception as e:
        logger.error(f"🔥 Fetch Attendance Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 📌 ATTENDANCE STATS
# =========================================================
@attendance_bp.route("/stats/<rollno>", methods=["GET"])
@login_required
def attendance_stats(rollno):

    rollno = rollno.strip().lower()

    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({"error": "Unauthorized"}), 403

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status='present') AS present,
                COUNT(*) AS total
            FROM attendance
            WHERE rollno = %s
        """, (rollno,))

        result = cursor.fetchone() or (0, 0)

        present = result[0] or 0
        total = result[1] or 0

        percentage = round((present / total) * 100, 2) if total else 0

        # 📊 ANALYSIS
        if percentage >= 75:
            remark = "Good attendance"
        elif percentage >= 50:
            remark = "Average attendance"
        else:
            remark = "Low attendance"

        return jsonify({
            "status": "success",
            "data": {
                "present": present,
                "total": total,
                "percentage": percentage,
                "remark": remark
            }
        }), 200

    except Exception as e:
        logger.error(f"🔥 Stats Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)