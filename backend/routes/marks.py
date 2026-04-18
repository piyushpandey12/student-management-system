from flask import Blueprint, jsonify, request
from backend.utils.db import get_connection, release_connection

marks_bp = Blueprint('marks', __name__)

# =========================================================
# 📌 ADD / UPDATE MARKS
# =========================================================
@marks_bp.route("/update", methods=["POST", "OPTIONS"])
def update_marks():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json() or {}

    rollno = data.get("rollno")
    subject = data.get("subject")
    marks = data.get("marks")
    teacher_id = data.get("teacher_id")

    # ✅ VALIDATION
    if not rollno or not subject or marks is None:
        return jsonify({
            "status": "error",
            "message": "rollno, subject, marks required"
        }), 400

    if not isinstance(marks, (int, float)) or marks < 0 or marks > 100:
        return jsonify({
            "status": "error",
            "message": "marks must be between 0 and 100"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

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
            "message": "Marks updated"
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
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 GET MARKS
# =========================================================
@marks_bp.route("/<rollno>", methods=["GET", "OPTIONS"])
def get_marks(rollno):

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT subject, marks, teacher_id
            FROM marks
            WHERE rollno = %s
        """, (rollno,))

        rows = cursor.fetchall()

        return jsonify([
            {
                "subject": r[0],
                "marks": r[1],
                "teacher_id": r[2]
            }
            for r in rows
        ])

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 MARKS STATS
# =========================================================
@marks_bp.route("/stats/<rollno>", methods=["GET", "OPTIONS"])
def marks_stats(rollno):

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

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

        avg_marks = float(result[0]) if result else 0
        max_marks = int(result[1]) if result else 0
        min_marks = int(result[2]) if result else 0
        total_subjects = int(result[3]) if result else 0

        return jsonify({
            "status": "success",
            "average": round(avg_marks, 2),
            "highest": max_marks,
            "lowest": min_marks,
            "subjects": total_subjects
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
            release_connection(db)   # ✅ FIXED