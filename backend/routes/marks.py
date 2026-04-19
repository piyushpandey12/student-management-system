# ================= IMPORTS =================
from flask import Blueprint, jsonify, request, g
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import login_required, role_required

marks_bp = Blueprint('marks', __name__)


# =========================================================
# 📌 ADD / UPDATE MARKS (SECURE)
# =========================================================
@marks_bp.route("/update", methods=["POST"])
@login_required
@role_required("teacher")   # 🔐 only teacher can update
def update_marks():

    data = request.get_json(silent=True) or {}

    rollno = (data.get("rollno") or "").strip()
    subject = (data.get("subject") or "").strip().lower()
    teacher_id = g.user.get("identifier")  # 🔥 from token

    # 🔁 convert marks safely
    try:
        marks = float(data.get("marks"))
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "marks must be a number"
        }), 400

    # ✅ VALIDATION
    if not rollno or not subject:
        return jsonify({
            "status": "error",
            "message": "rollno and subject required"
        }), 400

    if marks < 0 or marks > 100:
        return jsonify({
            "status": "error",
            "message": "marks must be between 0 and 100"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ CALL DB FUNCTION (BEST PRACTICE)
        cursor.execute(
            "SELECT update_marks(%s, %s, %s, %s)",
            (rollno, subject, marks, teacher_id)
        )

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Marks saved successfully"
        })

    except Exception as e:
        if db:
            db.rollback()

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
# 📌 GET MARKS (SECURE)
# =========================================================
@marks_bp.route("/<rollno>", methods=["GET"])
@login_required
def get_marks(rollno):

    # 🔐 student can only view own data
    if g.user["role"] == "student" and g.user["identifier"] != rollno:
        return jsonify({"error": "Unauthorized"}), 403

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT subject, marks, teacher_id
            FROM marks
            WHERE rollno = %s
            ORDER BY subject ASC
        """, (rollno,))

        rows = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": [
                {
                    "subject": r[0],
                    "marks": float(r[1]),
                    "teacher_id": r[2]
                }
                for r in rows
            ]
        })

    except Exception as e:
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
# 📌 MARKS STATS (WITH ANALYSIS)
# =========================================================
@marks_bp.route("/stats/<rollno>", methods=["GET"])
@login_required
def marks_stats(rollno):

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

        result = cursor.fetchone()

        avg_marks = float(result[0])
        max_marks = int(result[1])
        min_marks = int(result[2])
        total_subjects = int(result[3])

        # 🔥 ADD ANALYSIS
        if avg_marks >= 75:
            remark = "Excellent performance"
        elif avg_marks >= 50:
            remark = "Average performance"
        else:
            remark = "Needs improvement"

        return jsonify({
            "status": "success",
            "data": {
                "average": round(avg_marks, 2),
                "highest": max_marks,
                "lowest": min_marks,
                "subjects": total_subjects,
                "remark": remark
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)
