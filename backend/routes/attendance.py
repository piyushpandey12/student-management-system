from flask import Blueprint, jsonify, request
from backend.utils.db import get_connection, release_connection

attendance_bp = Blueprint('attendance', __name__)

# =========================================================
# 📌 MARK ATTENDANCE
# =========================================================
@attendance_bp.route("/mark", methods=["POST", "OPTIONS"])
def mark_attendance():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json() or {}

    rollno = data.get("rollno")
    date = data.get("date")
    status = data.get("status")
    teacher_id = data.get("teacher_id")  # optional

    # ✅ Validation
    if not rollno or not date or not status:
        return jsonify({
            "error": "rollno, date, status required"
        }), 400

    if status not in ["present", "absent"]:
        return jsonify({
            "error": "status must be 'present' or 'absent'"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO attendance (rollno, date, status, teacher_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, date)
            DO UPDATE SET 
                status = EXCLUDED.status,
                teacher_id = EXCLUDED.teacher_id
        """, (rollno, date, status, teacher_id))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Attendance saved"
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
# 📌 GET ATTENDANCE
# =========================================================
@attendance_bp.route("/<rollno>", methods=["GET", "OPTIONS"])
def get_attendance(rollno):

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT date, status
            FROM attendance
            WHERE rollno = %s
            ORDER BY date DESC
        """, (rollno,))

        rows = cursor.fetchall()

        return jsonify([
            {
                "date": str(r[0]),
                "status": r[1]
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
# 📌 ATTENDANCE STATS
# =========================================================
@attendance_bp.route("/stats/<rollno>", methods=["GET", "OPTIONS"])
def attendance_stats(rollno):

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status='present'),
                COUNT(*)
            FROM attendance
            WHERE rollno = %s
        """, (rollno,))

        result = cursor.fetchone()

        present = result[0] if result else 0
        total = result[1] if result else 0

        percentage = round((present / total) * 100, 2) if total else 0

        return jsonify({
            "status": "success",
            "present": present,
            "total": total,
            "percentage": percentage
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