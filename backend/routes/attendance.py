# =========================================================
# 📌 IMPORTS
# =========================================================
from flask import Blueprint, jsonify, request, g
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import login_required, role_required
from psycopg2.extras import RealDictCursor
import logging

attendance_bp = Blueprint('attendance', __name__)
logger = logging.getLogger(__name__)


# =========================================================
# 📌 MARK ATTENDANCE (FINAL CLEAN VERSION)
# =========================================================
@attendance_bp.route("/<rollno>", methods=["POST"])
@login_required
@role_required("teacher")
def mark_attendance(rollno):

    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip().lower()

    if status not in ["present", "absent"]:
        return jsonify({
            "status": "error",
            "message": "Status must be present or absent"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        rollno = rollno.strip().lower()
        teacher_id = g.user.get("identifier")

        # ✅ CHECK STUDENT
        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        # =========================================================
        # ✅ SAFE UPSERT (NO UNIQUE CONSTRAINT NEEDED)
        # =========================================================
        cursor.execute("""
            SELECT 1 FROM attendance 
            WHERE rollno=%s AND date=CURRENT_DATE
        """, (rollno,))

        if cursor.fetchone():
            # UPDATE
            cursor.execute("""
                UPDATE attendance
                SET status=%s, teacher_id=%s
                WHERE rollno=%s AND date=CURRENT_DATE
            """, (status, teacher_id, rollno))
        else:
            # INSERT
            cursor.execute("""
                INSERT INTO attendance (rollno, date, status, teacher_id)
                VALUES (%s, CURRENT_DATE, %s, %s)
            """, (rollno, status, teacher_id))

        db.commit()

        return jsonify({
            "status": "success",
            "message": f"{status.capitalize()} marked"
        }), 200

    except Exception as e:
        if db:
            db.rollback()

        logger.error(f"🔥 Attendance Error: {str(e)}")

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
# 📌 GET ATTENDANCE
# =========================================================
@attendance_bp.route("/<rollno>", methods=["GET"])
@login_required
def get_attendance(rollno):

    rollno = rollno.strip().lower()

    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({"error": "Unauthorized"}), 403

    db = get_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("""
            SELECT date, status
            FROM attendance
            WHERE rollno=%s
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
        cursor.close()
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

    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status='present') AS present,
                COUNT(*) AS total
            FROM attendance
            WHERE rollno=%s
        """, (rollno,))

        present, total = cursor.fetchone() or (0, 0)

        percentage = round((present / total) * 100, 2) if total else 0

        return jsonify({
            "status": "success",
            "data": {
                "present": present or 0,
                "total": total or 0,
                "percentage": percentage
            }
        }), 200

    except Exception as e:
        logger.error(f"🔥 Stats Error: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        release_connection(db)