from flask import Blueprint, request, jsonify
from utils.db import get_connection

students_bp = Blueprint("students", __name__)

# =========================================================
# 📌 GET ALL STUDENTS (FROM VIEW)
# =========================================================
@students_bp.route("/", methods=["GET"])
def get_students():
    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM student_dashboard")
        rows = cursor.fetchall()

        students = []
        for row in rows:
            students.append({
                "rollno": row[0],
                "name": row[1],
                "avg_marks": row[2],
                "present_days": row[3],
                "total_days": row[4],
                "attendance_percent": float(row[5])
            })

        return jsonify(students)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()


# =========================================================
# 📌 ADD STUDENT
# =========================================================
@students_bp.route("/", methods=["POST"])
def add_student():
    data = request.get_json()

    name = data.get("name")
    rollno = data.get("rollno")

    if not name or not rollno:
        return jsonify({"error": "Name & RollNo required"}), 400

    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if cursor.fetchone():
            return jsonify({"error": "Student already exists"}), 409

        cursor.execute(
            "INSERT INTO students (rollno, name) VALUES (%s, %s)",
            (rollno, name)
        )

        cursor.execute(
            "INSERT INTO users (rollno, password, role) VALUES (%s, %s, %s)",
            (rollno, "default123", "student")
        )

        db.commit()

        return jsonify({"message": "Student added"}), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
@students_bp.route("/<rollno>", methods=["DELETE"])
def delete_student(rollno):
    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT rollno FROM students WHERE rollno=%s", (rollno,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        cursor.execute("DELETE FROM students WHERE rollno=%s", (rollno,))
        cursor.execute("DELETE FROM users WHERE rollno=%s", (rollno,))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Deleted successfully"
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()


# =========================================================
# 📌 STUDENT DASHBOARD (FINAL FIX)
# =========================================================
@students_bp.route("/dashboard/<rollno>", methods=["GET"])
def student_dashboard(rollno):

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 📊 MARKS
        cursor.execute("""
            SELECT subject, marks 
            FROM marks 
            WHERE rollno=%s
        """, (rollno,))
        marks_rows = cursor.fetchall()

        marks = [
            {"subject": m[0], "marks": m[1]}
            for m in marks_rows
        ]

        # 📅 ATTENDANCE
        cursor.execute("""
            SELECT status 
            FROM attendance 
            WHERE rollno=%s
        """, (rollno,))
        attendance_rows = cursor.fetchall()

        present = sum(1 for a in attendance_rows if a[0] == "present")
        total = len(attendance_rows)

        attendance_percent = round((present / total) * 100, 2) if total else 0

        return jsonify({
            "status": "success",
            "marks": marks,
            "attendance_percent": attendance_percent,
            "total_days": total,
            "present_days": present
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()