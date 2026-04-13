from flask import Blueprint, jsonify, request
from utils.db import get_connection

attendance_bp = Blueprint('attendance', __name__)


# =========================================================
# 📌 MARK ATTENDANCE
# =========================================================
@attendance_bp.route("/", methods=["POST", "OPTIONS"])
def mark_attendance():

    # 🔥 HANDLE PREFLIGHT
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()

    student_id = data.get("student_id") if data else None
    total = data.get("total", 1) if data else 1
    attended = data.get("attended", 1) if data else 1

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ UPSERT
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
        if db:
            db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 GET ATTENDANCE %
# =========================================================
@attendance_bp.route("/", methods=["GET", "OPTIONS"])
def get_attendance():

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
@attendance_bp.route("/stats", methods=["GET", "OPTIONS"])
def attendance_stats():

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