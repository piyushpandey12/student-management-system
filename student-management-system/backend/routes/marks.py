from flask import Blueprint, jsonify, request
from utils.db import get_connection

# ================= CREATE BLUEPRINT =================
marks_bp = Blueprint('marks', __name__)


# =========================================================
# 📌 ADD / UPDATE MARKS
# =========================================================
@marks_bp.route("/", methods=["POST", "OPTIONS"])
def add_marks():

    # 🔥 HANDLE PREFLIGHT
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()

    student_id = data.get("student_id") if data else None
    marks = data.get("marks") if data else None

    if not student_id or marks is None:
        return jsonify({
            "status": "error",
            "message": "student_id and marks required"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 🔍 CHECK IF EXISTS
        cursor.execute(
            "SELECT 1 FROM marks WHERE student_id=%s",
            (student_id,)
        )

        if cursor.fetchone():
            cursor.execute(
                "UPDATE marks SET marks=%s WHERE student_id=%s",
                (marks, student_id)
            )
        else:
            cursor.execute(
                "INSERT INTO marks (student_id, marks) VALUES (%s, %s)",
                (student_id, marks)
            )

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
# 📌 GET MARKS STATS
# =========================================================
@marks_bp.route("/stats", methods=["GET", "OPTIONS"])
def stats():

    # 🔥 HANDLE PREFLIGHT
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
                COALESCE(MAX(marks), 0)
            FROM marks
        """)

        result = cursor.fetchone()

        avg_marks = float(result[0]) if result else 0
        top_score = int(result[1]) if result else 0

        return jsonify({
            "avg_marks": round(avg_marks, 2),
            "top_score": top_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()