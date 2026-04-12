from flask import Blueprint, jsonify, request
from utils.db import get_connection  # ✅ renamed for consistency

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
        db = get_connection()
        cursor = db.cursor()

        # ✅ PostgreSQL UPSERT (IMPORTANT CHANGE)
        cursor.execute("""
            INSERT INTO attendance (student_id, total_classes, attended_classes)
            VALUES (%s, %s, %s)
            ON CONFLICT (student_id)
            DO UPDATE SET
                total_classes = attendance.total_classes + EXCLUDED.total_classes,
                attended_classes = attendance.attended_classes + EXCLUDED.attended_classes
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
        db = get_connection()
        cursor = db.cursor()

        # ✅ IFNULL → COALESCE
        cursor.execute("""
            SELECT 
                COALESCE(
                    ROUND(SUM(attended_classes) * 100.0 / NULLIF(SUM(total_classes), 0), 2),
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
        db = get_connection()

        # ✅ PostgreSQL dict cursor
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_classes), 0),
                COALESCE(SUM(attended_classes), 0)
            FROM attendance
        """)

        result = cursor.fetchone()

        total = result[0]
        attended = result[1]

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