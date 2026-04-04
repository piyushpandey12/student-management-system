from flask import Blueprint, request, jsonify
from utils.db import get_connection

student_bp = Blueprint('student', __name__)


# ================= GET ALL STUDENTS =================
@student_bp.route('/', methods=['GET'])
def get_students():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        return jsonify(students)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ================= ADD STUDENT =================
@student_bp.route('/', methods=['POST'])
def add_student():
    data = request.get_json()

    rollno = data.get("rollno")
    name = data.get("name")
    email = data.get("email")

    if not rollno or not name:
        return jsonify({"error": "Missing required fields"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO students (rollno, name, email) VALUES (%s, %s, %s)",
            (rollno, name, email)
        )

        db.commit()

        return jsonify({"status": "student added"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()