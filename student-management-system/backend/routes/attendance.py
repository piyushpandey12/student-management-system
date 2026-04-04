from flask import Blueprint, jsonify, request
import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

attendance_bp = Blueprint('attendance', __name__)


# ================= DB CONNECTION =================
def get_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )


# ================= MARK ATTENDANCE =================
@attendance_bp.route("/", methods=["POST"])
def mark_attendance():
    data = request.json

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO attendance (student_id, total_classes, attended_classes)
        VALUES (%s, %s, %s)
        """,
        (data["student_id"], data["total"], data["attended"])
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Attendance recorded"})


# ================= GET ATTENDANCE % =================
@attendance_bp.route("/attendance", methods=["GET"])
def get_attendance():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
        COALESCE(
            (SUM(attended_classes) * 100.0) / NULLIF(SUM(total_classes), 0),
            0
        ) AS percentage
        FROM attendance
    """)

    result = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return jsonify({"attendance": float(result)})


# ================= DASHBOARD STATS =================
@attendance_bp.route("/stats", methods=["GET"])
def attendance_stats():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            SUM(total_classes) AS total_classes,
            SUM(attended_classes) AS attended_classes
        FROM attendance
    """)

    result = cursor.fetchone()

    cursor.close()
    db.close()

    total = result["total_classes"] or 0
    attended = result["attended_classes"] or 0

    percentage = round((attended / total) * 100, 2) if total else 0

    return jsonify({
        "attendance_percentage": percentage
    })