from flask import Blueprint, jsonify, request
from utils.db import get_db_connection

attendance_bp = Blueprint('attendance', __name__)


# ================= MARK ATTENDANCE =================
@attendance_bp.route("/", methods=["POST"])
def mark_attendance():
    data = request.get_json()

    student_id = data.get("student_id")
    total = data.get("total")
    attended = data.get("attended")

    if not student_id or total is None or attended is None:
        return jsonify({"error": "Missing fields"}), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO attendance (student_id, total_classes, attended_classes)
            VALUES (%s, %s, %s)
            """,
            (student_id, total, attended)
        )

        db.commit()

        return jsonify({"message": "Attendance recorded"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ================= GET ATTENDANCE % =================
@attendance_bp.route("/attendance", methods=["GET"])
def get_attendance():
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
            COALESCE(
                (SUM(attended_classes) * 100.0) / NULLIF(SUM(total_classes), 0),
                0
            ) AS percentage
            FROM attendance
        """)

        result = cursor.fetchone()
        percentage = float(result[0]) if result and result[0] else 0

        return jsonify({"attendance": percentage})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ================= DASHBOARD STATS =================
@attendance_bp.route("/stats", methods=["GET"])
def attendance_stats():
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                SUM(total_classes) AS total_classes,
                SUM(attended_classes) AS attended_classes
            FROM attendance
        """)

        result = cursor.fetchone()

        total = result["total_classes"] or 0
        attended = result["attended_classes"] or 0

        percentage = round((attended / total) * 100, 2) if total else 0

        return jsonify({
            "attendance_percentage": percentage
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()