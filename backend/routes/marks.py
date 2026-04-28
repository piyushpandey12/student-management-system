# =========================================================
# 📌 IMPORTS
# =========================================================
from flask import Blueprint, jsonify, request, g
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import login_required, role_required
from psycopg2.extras import RealDictCursor
import logging

marks_bp = Blueprint("marks", __name__)
logger = logging.getLogger(__name__)


# =========================================================
# 📌 ADD / UPDATE MARKS (FINAL FIXED)
# =========================================================
@marks_bp.route("/<rollno>", methods=["POST"])
@login_required
@role_required("teacher")
def save_marks(rollno):

    data = request.get_json(silent=True) or {}
    marks_list = data.get("marks", [])

    if not marks_list:
        return jsonify({
            "status": "error",
            "message": "No marks provided"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        rollno = rollno.strip().lower()
        teacher_id = g.user.get("identifier")

        # 🔒 CHECK STUDENT
        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        # =========================================================
        # 🔁 LOOP ALL SUBJECTS
        # =========================================================
        for m in marks_list:
            subject = (m.get("subject") or "").strip().lower()

            try:
                marks = int(m.get("marks"))
            except:
                continue

            if not subject or not (0 <= marks <= 100):
                continue

            # 🔁 CHECK EXISTING
            cursor.execute("""
                SELECT 1 FROM marks 
                WHERE rollno=%s AND subject=%s
            """, (rollno, subject))

            if cursor.fetchone():
                # 🔄 UPDATE
                cursor.execute("""
                    UPDATE marks
                    SET marks=%s, teacher_id=%s
                    WHERE rollno=%s AND subject=%s
                """, (marks, teacher_id, rollno, subject))
            else:
                # ➕ INSERT
                cursor.execute("""
                    INSERT INTO marks (rollno, subject, marks, teacher_id)
                    VALUES (%s, %s, %s, %s)
                """, (rollno, subject, marks, teacher_id))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Marks saved successfully"
        }), 200

    except Exception as e:
        if db:
            db.rollback()

        logger.error(f"🔥 SAVE MARKS ERROR: {str(e)}")

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
            WHERE rollno=%s
            ORDER BY subject
        """, (rollno,))

        return jsonify({
            "status": "success",
            "data": cursor.fetchall()
        }), 200

    except Exception as e:
        logger.error(f"🔥 FETCH MARKS ERROR: {str(e)}")

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
# 📊 MARKS STATS
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
            WHERE rollno=%s
        """, (rollno,))

        avg, max_m, min_m, total = cursor.fetchone()

        avg = float(avg)
        max_m = int(max_m)
        min_m = int(min_m)
        total = int(total)

        remark = (
            "Excellent" if avg >= 75 else
            "Average" if avg >= 50 else
            "Needs Improvement"
        )

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
        logger.error(f"🔥 STATS ERROR: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)