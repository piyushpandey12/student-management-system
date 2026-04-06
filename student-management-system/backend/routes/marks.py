from flask import Blueprint, jsonify, request
from utils.db import get_connection

marks_bp = Blueprint('marks', __name__)


# =========================================================
# 📌 ADD / UPDATE MARKS (UPSERT FIX 🔥)
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

        # 🔥 UPSERT (IMPORTANT FIX)
        cursor.execute("""
            INSERT INTO marks (student_id, subject, marks)
            VALUES (%s, 'General', %s)
            ON DUPLICATE KEY UPDATE
                marks = VALUES(marks)
        """, (student_id, marks))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Marks saved"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 GET MARKS STATS (SIMPLE)
# =========================================================
@marks_bp.route("/", methods=["GET"])
def get_marks():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                IFNULL(AVG(marks), 0),
                IFNULL(MAX(marks), 0)
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
# 📌 DASHBOARD STATS (ADVANCED)
# =========================================================
@marks_bp.route("/stats", methods=["GET"])
def marks_stats():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                IFNULL(AVG(marks), 0) AS avg_marks,
                IFNULL(MAX(marks), 0) AS top_score,
                IFNULL(MIN(marks), 0) AS lowest_score,
                COUNT(*) AS total_entries
            FROM marks
        """)

        result = cursor.fetchone()

        return jsonify({
            "status": "success",
            "avg_marks": round(result["avg_marks"], 2),
            "top_score": result["top_score"],
            "lowest_score": result["lowest_score"],
            "total_entries": result["total_entries"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()