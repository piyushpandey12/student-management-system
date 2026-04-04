from flask import Blueprint, jsonify, request
import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

marks_bp = Blueprint('marks', __name__)


# ================= DB CONNECTION =================
def get_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )


# ================= ADD MARKS =================
@marks_bp.route("/", methods=["POST"])
def add_marks():
    data = request.json

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO marks (student_id, subject, marks)
        VALUES (%s, %s, %s)
        """,
        (data["student_id"], data["subject"], data["marks"])
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Marks added"})


# ================= UPDATE MARKS =================
@marks_bp.route("/<int:id>", methods=["PUT"])
def update_marks(id):
    data = request.json

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE marks SET marks=%s WHERE id=%s",
        (data["marks"], id)
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Marks updated"})


# ================= SIMPLE MARKS API =================
@marks_bp.route("/marks", methods=["GET"])
def get_marks():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            COALESCE(AVG(marks), 0),
            COALESCE(MAX(marks), 0)
        FROM marks
    """)

    avg, top = cursor.fetchone()

    cursor.close()
    db.close()

    return jsonify({
        "average": float(avg),
        "top": int(top)
    })


# ================= DASHBOARD STATS =================
@marks_bp.route("/stats", methods=["GET"])
def marks_stats():
    db = get_db()
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

    cursor.close()
    db.close()

    return jsonify({
        "avg_marks": round(result["avg_marks"], 2),
        "top_score": result["top_score"],
        "lowest_score": result["lowest_score"],
        "total_entries": result["total_entries"]
    })