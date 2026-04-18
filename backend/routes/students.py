from flask import Blueprint, request, jsonify
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import hash_password

students_bp = Blueprint("students", __name__)

# =========================================================
# 📌 GET ALL STUDENTS
# =========================================================
@students_bp.route("/", methods=["GET"])
def get_students():

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM student_dashboard")
        rows = cursor.fetchall()

        students = [
            {
                "rollno": row[0],
                "name": row[1],
                "avg_marks": float(row[2]),
                "present_days": row[3],
                "total_days": row[4],
                "attendance_percent": float(row[5])
            }
            for row in rows
        ]

        return jsonify(students)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 ADD STUDENT
# =========================================================
@students_bp.route("/", methods=["POST"])
def add_student():

    data = request.get_json() or {}

    name = data.get("name")
    rollno = data.get("rollno")

    if not name or not rollno:
        return jsonify({"error": "Name & RollNo required"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if cursor.fetchone():
            return jsonify({"error": "Student already exists"}), 409

        # ✅ insert student
        cursor.execute("""
            INSERT INTO students (rollno, name)
            VALUES (%s, %s)
        """, (rollno, name))

        # ✅ insert user (secure)
        cursor.execute("""
            INSERT INTO users (identifier, password, role)
            VALUES (%s, %s, %s)
        """, (rollno, hash_password("default123"), "student"))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Student added"
        }), 201

    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
@students_bp.route("/<rollno>", methods=["DELETE"])
def delete_student(rollno):

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT rollno FROM students WHERE rollno=%s", (rollno,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        cursor.execute("DELETE FROM students WHERE rollno=%s", (rollno,))
        cursor.execute("DELETE FROM users WHERE identifier=%s", (rollno,))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Deleted successfully"
        })

    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 STUDENT DASHBOARD
# =========================================================
@students_bp.route("/dashboard/<rollno>", methods=["GET"])
def student_dashboard(rollno):

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # MARKS
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

        # ATTENDANCE
        cursor.execute("""
            SELECT status 
            FROM attendance 
            WHERE rollno=%s
        """, (rollno,))
        attendance_rows = cursor.fetchall()

        present = sum(1 for a in attendance_rows if a[0] == "present")
        total = len(attendance_rows)

        attendance_percent = round((present / total) * 100, 2) if total else 0

        # STUDENT INFO
        cursor.execute("""
            SELECT name FROM students WHERE rollno=%s
        """, (rollno,))
        student = cursor.fetchone()

        return jsonify({
            "status": "success",
            "name": student[0] if student else "",
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
            release_connection(db)   # ✅ FIXED