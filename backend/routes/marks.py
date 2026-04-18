from flask import Blueprint, jsonify, request
from backend.utils.db import get_connection

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

    if not rollno or not subject or marks is None:
        return jsonify({
            "status": "error",
            "message": "rollno, subject, marks required"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO marks (rollno, subject, marks)
            VALUES (%s, %s, %s)
            ON CONFLICT (rollno, subject)
            DO UPDATE SET marks = EXCLUDED.marks
        """, (rollno, subject, marks))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Marks updated"
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
            SELECT subject, marks
            FROM marks
            WHERE rollno = %s
        """, (rollno,))

        rows = cursor.fetchall()

        return jsonify([
            {"subject": r[0], "marks": r[1]}
            for r in rows
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


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
                COALESCE(MAX(marks), 0)
            FROM marks
            WHERE rollno = %s
        """, (rollno,))

        result = cursor.fetchone()

        avg_marks = float(result[0]) if result else 0
        top_score = int(result[1]) if result else 0

        return jsonify({
            "status": "success",
            "average": round(avg_marks, 2),
            "highest": top_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()