from flask import Blueprint, request, jsonify
from utils.db import get_connection

students_bp = Blueprint("students", __name__)

# =========================================================
# 📌 GET ALL STUDENTS (USING VIEW - BEST PRACTICE)
# =========================================================
@students_bp.route('/students', methods=['GET'])
def get_students():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ Using VIEW (clean & fast)
        cursor.execute("SELECT * FROM student_dashboard")
        rows = cursor.fetchall()

        students = []
        for row in rows:
            students.append({
                "id": row[0],
                "name": row[1],
                "roll": row[2],
                "marks": row[3],
                "attendance": bool(row[4])
            })

        return jsonify(students)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if db: db.close()


# =========================================================
# 📌 ADD STUDENT
# =========================================================
@students_bp.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    name = data.get("name")
    roll = data.get("roll")
    marks = data.get("marks", 0)

    if not name or not roll:
        return jsonify({"error": "Name & Roll required"}), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # ✅ PostgreSQL: RETURNING id
        cursor.execute(
            "INSERT INTO students (rollno, name) VALUES (%s, %s) RETURNING id",
            (roll, name)
        )
        student_id = cursor.fetchone()[0]

        # Insert marks
        cursor.execute(
            "INSERT INTO marks (student_id, marks) VALUES (%s, %s)",
            (student_id, marks)
        )

        # Insert attendance
        cursor.execute(
            "INSERT INTO attendance (student_id, attended_classes) VALUES (%s, %s)",
            (student_id, 0)
        )

        db.commit()

        return jsonify({"msg": "Student added"})

    except Exception as e:
        if db: db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if db: db.close()


# =========================================================
# 📌 UPDATE STUDENT
# =========================================================
@students_bp.route('/students/<roll>', methods=['PUT'])
def update_student(roll):
    data = request.get_json()

    name = data.get("name")
    marks = data.get("marks", 0)
    attendance = data.get("attendance", False)

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # Get student id
        cursor.execute("SELECT id FROM students WHERE rollno=%s", (roll,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Student not found"}), 404

        student_id = result[0]

        # Update name
        cursor.execute(
            "UPDATE students SET name=%s WHERE id=%s",
            (name, student_id)
        )

        # Update marks
        cursor.execute(
            "UPDATE marks SET marks=%s WHERE student_id=%s",
            (marks, student_id)
        )

        # Update attendance (boolean → 0/1)
        cursor.execute(
            "UPDATE attendance SET attended_classes=%s WHERE student_id=%s",
            (1 if attendance else 0, student_id)
        )

        db.commit()

        return jsonify({"msg": "Student updated"})

    except Exception as e:
        if db: db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if db: db.close()


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
@students_bp.route('/students/<roll>', methods=['DELETE'])
def delete_student(roll):
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # Get student id
        cursor.execute("SELECT id FROM students WHERE rollno=%s", (roll,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Student not found"}), 404

        student_id = result[0]

        # Delete related data first
        cursor.execute("DELETE FROM marks WHERE student_id=%s", (student_id,))
        cursor.execute("DELETE FROM attendance WHERE student_id=%s", (student_id,))
        cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))

        db.commit()

        return jsonify({"msg": "Student deleted"})

    except Exception as e:
        if db: db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if db: db.close()