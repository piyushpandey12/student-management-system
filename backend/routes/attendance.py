from flask import Blueprint, jsonify, request
from backend.utils.db import get_connection   # ✅ FIXED

attendance_bp = Blueprint('attendance', __name__)

# =========================================================
# 📌 MARK ATTENDANCE (SUBJECT + DATE-WISE)
# =========================================================
@attendance_bp.route("/mark", methods=["POST", "OPTIONS"])
def mark_attendance():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()

    rollno = data.get("rollno")
    subject = data.get("subject")
    date = data.get("date")
    status = data.get("status")

    if not rollno or not subject or not date or not status:
        return jsonify({
            "error": "rollno, subject, date, status required"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO attendance (rollno, subject, date, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, subject, date)
            DO UPDATE SET status = EXCLUDED.status
        """, (rollno, subject, date, status))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Attendance saved"
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
            SELECT subject, date, status
            FROM attendance
            WHERE rollno = %s
            ORDER BY date DESC
        """, (rollno,))

        rows = cursor.fetchall()

        return jsonify([
            {
                "subject": r[0],
                "date": str(r[1]),
                "status": r[2]
            }
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
# 📌 ATTENDANCE STATS
# =========================================================
@attendance_bp.route("/stats/<rollno>", methods=["GET", "OPTIONS"])
def attendance_stats(rollno):

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    subject = request.args.get("subject")

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        if subject:
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE status='present'),
                    COUNT(*)
                FROM attendance
                WHERE rollno = %s AND subject = %s
            """, (rollno, subject))
        else:
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
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()