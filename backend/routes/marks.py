# =========================================================
# 📌 IMPORTS
# =========================================================
from flask import Blueprint, jsonify, request, g
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import login_required, role_required
from psycopg2.extras import RealDictCursor
import logging

marks_bp = Blueprint('marks', __name__)
logger = logging.getLogger(__name__)


# =========================================================
# 📌 ADD / UPDATE MARKS (FIXED)
# =========================================================
@marks_bp.route("/update", methods=["POST"])
@login_required
@role_required("teacher")
def update_marks():

    data = request.get_json(silent=True) or {}

    rollno = (data.get("rollno") or "").strip().lower()
    subject = (data.get("subject") or "").strip().lower()
    teacher_id = g.user.get("identifier")

    # 🔁 SAFE PARSE
    try:
        marks = int(data.get("marks"))
    except (TypeError, ValueError):
        return jsonify({"error": "marks must be a number"}), 400

    # ✅ VALIDATION
    if not rollno or not subject:
        return jsonify({"error": "rollno and subject required"}), 400

    if not (0 <= marks <= 100):
        return jsonify({"error": "marks must be between 0 and 100"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 🔒 CHECK STUDENT EXISTS
        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        # ✅ UPSERT (PER SUBJECT)
        cursor.execute("""
            INSERT INTO marks (rollno, subject, marks, teacher_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, subject)
            DO UPDATE SET
                marks = EXCLUDED.marks,
                teacher_id = EXCLUDED.teacher_id
        """, (rollno, subject, marks, teacher_id))

        db.commit()

        return jsonify({
            "status": "success",
            "message": f"Marks saved for {subject}"
        }), 200

    except Exception as e:
        if db:
            db.rollback()

        logger.error(f"🔥 Marks Error: {str(e)}")

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
# 📌 GET MARKS
# =========================================================
@marks_bp.route("/<rollno>", methods=["GET"])
@login_required
def get_marks(rollno):

    rollno = rollno.strip().lower()

    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({"error": "Unauthorized"}), 403

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT subject, marks, teacher_id
            FROM marks
            WHERE rollno = %s
            ORDER BY subject ASC
        """, (rollno,))

        return jsonify({
            "status": "success",
            "data": cursor.fetchall()
        }), 200

    except Exception as e:
        logger.error(f"🔥 Fetch Marks Error: {str(e)}")

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
# 📌 MARKS STATS
# =========================================================
@marks_bp.route("/stats/<rollno>", methods=["GET"])
@login_required
def marks_stats(rollno):

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
                COALESCE(AVG(marks), 0),
                COALESCE(MAX(marks), 0),
                COALESCE(MIN(marks), 0),
                COUNT(*)
            FROM marks
            WHERE rollno = %s
        """, (rollno,))

        avg, max_m, min_m, total = cursor.fetchone()

        avg = float(avg)
        max_m = int(max_m)
        min_m = int(min_m)
        total = int(total)

        if avg >= 75:
            remark = "Excellent"
        elif avg >= 50:
            remark = "Average"
        else:
            remark = "Needs Improvement"

        return jsonify({
            "status": "success",
            "data": {
                "average": round(avg, 2),
                "highest": max_m,
                "lowest": min_m,
                "subjects": total,
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