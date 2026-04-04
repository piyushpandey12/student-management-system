from flask import Blueprint, jsonify, request
from utils.db import get_db_connection

marks_bp = Blueprint('marks', __name__)


# ================= ADD MARKS =================
@marks_bp.route("/", methods=["POST"])
def add_marks():
    data = request.get_json()

    student_id = data.get("student_id")
    subject = data.get("subject")
    marks = data.get("marks")

    if not student_id or not subject or marks is None:
        return jsonify({"error": "Missing fields"}), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO marks (student_id, subject, marks)
            VALUES (%s, %s, %s)
            """,
            (student_id, subject, marks)
        )

        db.commit()

        return jsonify({"message": "Marks added"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ================= UPDATE MARKS =================
@marks_bp.route("/<int:id>", methods=["PUT"])
def update_marks(id):
    data = request.get_json()
    marks = data.get("marks")

    if marks is None:
        return jsonify({"error": "Marks value required"}), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "UPDATE marks SET marks=%s WHERE id=%s",
            (marks, id)
        )

        db.commit()

        return jsonify({"message": "Marks updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ================= SIMPLE MARKS API =================
@marks_bp.route("/marks", methods=["GET"])
def get_marks():
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                COALESCE(AVG(marks), 0),
                COALESCE(MAX(marks), 0)
            FROM marks
        """)

        result = cursor.fetchone()
        avg = float(result[0]) if result and result[0] else 0
        top = int(result[1]) if result and result[1] else 0

        return jsonify({
            "average": avg,
            "top": top
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ================= DASHBOARD STATS =================
@marks_bp.route("/stats", methods=["GET"])
def marks_stats():
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                COALESCE(AVG(marks), 0) AS avg_marks,
                COALESCE(MAX(marks), 0) AS top_score,
                COALESCE(MIN(marks), 0) AS lowest_score,
                COUNT(*) AS total_entries
            FROM marks
        """)

        result = cursor.fetchone()

        return jsonify({
            "avg_marks": round(result["avg_marks"], 2) if result["avg_marks"] else 0,
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