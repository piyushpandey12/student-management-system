from flask import Blueprint, jsonify, request
from utils.db import get_connection   # ✅ updated

marks_bp = Blueprint('marks', __name__)


# =========================================================
# 📌 ADD / UPDATE MARKS
# =========================================================
@marks_bp.route("/", methods=["POST"])
def add_or_update_marks():
    data = request.get_json()

    student_id = data.get("student_id")
    marks = data.get("marks")

    if not student_id or marks is None:
        return jsonify({"error": "student_id and marks required"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ PostgreSQL UPSERT
        cursor.execute("""
            INSERT INTO marks (student_id, subject, marks)
            VALUES (%s, 'General', %s)
            ON CONFLICT (student_id, subject)
            DO UPDATE SET
                marks = EXCLUDED.marks
        """, (student_id, marks))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Marks saved"
        })

    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 GET MARKS
# =========================================================
@marks_bp.route("/", methods=["GET"])
def get_marks():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ IFNULL → COALESCE
        cursor.execute("""
            SELECT 
                COALESCE(AVG(marks), 0),
                COALESCE(MAX(marks), 0)
            FROM marks
        """)

        result = cursor.fetchone()

        avg = float(result[0]) if result else 0
        top = int(result[1]) if result else 0

        return jsonify({
            "avg_marks": round(avg, 2),
            "top_score": top
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 DASHBOARD STATS
# =========================================================
@marks_bp.route("/stats", methods=["GET"])
def marks_stats():
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
        """)

        result = cursor.fetchone()

        avg_marks = float(result[0])
        top_score = result[1]
        lowest_score = result[2]
        total_entries = result[3]

        return jsonify({
            "status": "success",
            "avg_marks": round(avg_marks, 2),
            "top_score": top_score,
            "lowest_score": lowest_score,
            "total_entries": total_entries
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()