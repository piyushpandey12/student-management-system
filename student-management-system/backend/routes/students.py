from flask import Blueprint, request, jsonify
from utils.db import get_connection

# ================= CREATE BLUEPRINT =================
students_bp = Blueprint("students", __name__)


# =========================================================
# 📌 GET ALL STUDENTS
# URL: /api/students/
# =========================================================
@students_bp.route("/", methods=["GET"])
def get_students():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ Using VIEW (recommended)
        cursor.execute("SELECT * FROM student_dashboard")
        rows = cursor.fetchall()

        students = []
        for row in rows:
            students.append({
                "id": row[0],
                "name": row[1],
                "rollno": row[2],   # ✅ FIXED (was roll)
                "marks": row[3],
                "attendance": bool(row[4])
            })

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
# URL: /api/students/
# =========================================================
@students_bp.route("/", methods=["POST"])
def add_student():
    data = request.get_json()

    name = data.get("name") if data else None
    rollno = data.get("rollno") if data else None
    marks = data.get("marks", 0) if data else 0

    if not name or not rollno:
        return jsonify({"error": "Name & RollNo required"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 🔍 CHECK duplicate
        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if cursor.fetchone():
            return jsonify({"error": "Student already exists"}), 409

        # ✅ INSERT STUDENT
        cursor.execute(
            "INSERT INTO students (rollno, name) VALUES (%s, %s) RETURNING id",
            (rollno, name)
        )
        student_id = cursor.fetchone()[0]

        # ✅ INSERT MARKS
        cursor.execute(
            "INSERT INTO marks (student_id, marks) VALUES (%s, %s)",
            (student_id, marks)
        )

        # ✅ INSERT ATTENDANCE
        cursor.execute(
            "INSERT INTO attendance (student_id, total_classes, attended_classes) VALUES (%s, %s, %s)",
            (student_id, 0, 0)
        )

        db.commit()

        return jsonify({
            "status": "success",
            "id": student_id
        }), 201

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
# 📌 DELETE STUDENT (BY ID)
# URL: /api/students/<id>
# =========================================================
@students_bp.route("/<int:id>", methods=["DELETE"])
def delete_student(id):
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 🔍 CHECK EXISTS
        cursor.execute("SELECT id FROM students WHERE id=%s", (id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Student not found"}), 404

        # ✅ DELETE RELATED DATA FIRST
        cursor.execute("DELETE FROM marks WHERE student_id=%s", (id,))
        cursor.execute("DELETE FROM attendance WHERE student_id=%s", (id,))
        cursor.execute("DELETE FROM students WHERE id=%s", (id,))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Student deleted"
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