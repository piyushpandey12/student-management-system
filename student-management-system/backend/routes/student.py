from flask import Blueprint, request, jsonify
from utils.db import get_connection

student_bp = Blueprint('student', __name__)


# =========================================================
# 📌 GET ALL STUDENTS (JOIN WITH MARKS + ATTENDANCE 🔥)
# =========================================================
@student_bp.route('/', methods=['GET'])
def get_students():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                s.id,
                s.name,
                s.rollno AS roll,

                COALESCE(m.marks, 0) AS marks,

                CASE 
                    WHEN a.attended_classes > 0 THEN TRUE
                    ELSE FALSE
                END AS attendance

            FROM students s
            LEFT JOIN marks m ON s.id = m.student_id
            LEFT JOIN attendance a ON s.id = a.student_id
        """)

        students = cursor.fetchall()

        return jsonify(students)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 ADD STUDENT
# =========================================================
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

        return jsonify({
            "status": "success",
            "message": "Student added"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
@student_bp.route('/<int:id>', methods=['DELETE'])
def delete_student(id):
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("DELETE FROM students WHERE id=%s", (id,))
        db.commit()

        return jsonify({
            "status": "success",
            "message": "Student deleted"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()