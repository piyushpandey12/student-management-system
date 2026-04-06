from flask import Blueprint, jsonify, request
from utils.db import get_db_connection

attendance_bp = Blueprint('attendance', __name__)


# =========================================================
# 📌 MARK ATTENDANCE
# =========================================================
@attendance_bp.route("/", methods=["POST"])
def mark_attendance():
    data = request.get_json()

    student_id = data.get("student_id")
    total = data.get("total", 1)
    attended = data.get("attended", 1)

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()   # ✅ FIXED
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO attendance (student_id, total_classes, attended_classes)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_classes = total_classes + VALUES(total_classes),
                attended_classes = attended_classes + VALUES(attended_classes)
        """, (student_id, total, attended))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Attendance updated"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 GET ATTENDANCE %
# =========================================================
@attendance_bp.route("/", methods=["GET"])
def get_attendance():
    db = None
    cursor = None

    try:
        db = get_db_connection()   # ✅ FIXED
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                IFNULL(
                    ROUND(SUM(attended_classes) / SUM(total_classes) * 100, 2),
                    0
                )
            FROM attendance
        """)

        result = cursor.fetchone()
        percentage = float(result[0]) if result and result[0] else 0

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


# =========================================================
# 📌 DASHBOARD STATS
# =========================================================
@attendance_bp.route("/stats", methods=["GET"])
def attendance_stats():
    db = None
    cursor = None

    try:
        db = get_db_connection()   # ✅ FIXED
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                IFNULL(SUM(total_classes), 0) AS total_classes,
                IFNULL(SUM(attended_classes), 0) AS attended_classes
            FROM attendance
        """)

        result = cursor.fetchone()

        total = result["total_classes"]
        attended = result["attended_classes"]

        percentage = round((attended / total) * 100, 2) if total else 0

        return jsonify({
            "status": "success",
            "attendance_percentage": percentage,
            "total_classes": total,
            "attended_classes": attended
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()