# =========================================
# 📌 IMPORTS
# =========================================
import psycopg2
import os
from datetime import date
from psycopg2.extras import RealDictCursor


# =========================================
# 🔌 DATABASE CONNECTION
# =========================================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "student_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password")
    )


# =========================================
# ✅ CREATE STUDENT
# =========================================
def create_student(name, rollno, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        rollno = rollno.strip().lower()

        # 🔹 Check if already exists
        cur.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if cur.fetchone():
            return {"error": "Student already exists"}, 400

        # 🔹 Insert
        cur.execute(
            """
            INSERT INTO students (rollno, name, password)
            VALUES (%s, %s, %s)
            """,
            (rollno, name, password)
        )

        conn.commit()
        return {"message": "Student added successfully"}, 201

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ GET ALL STUDENTS
# =========================================
def get_all_students():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("SELECT rollno, name FROM students ORDER BY rollno")
        students = cur.fetchall()

        # 🔹 calculate avg marks
        for s in students:
            cur.execute(
                "SELECT AVG(marks) FROM marks WHERE rollno=%s",
                (s["rollno"],)
            )
            avg = cur.fetchone()["avg"] or 0
            s["avg_marks"] = round(avg, 2)

        return {"data": students}, 200

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ DELETE STUDENT
# =========================================
def delete_student(rollno):
    conn = get_connection()
    cur = conn.cursor()

    try:
        rollno = rollno.strip().lower()

        cur.execute("DELETE FROM students WHERE rollno=%s", (rollno,))

        if cur.rowcount == 0:
            return {"error": "Student not found"}, 404

        conn.commit()
        return {"message": "Deleted successfully"}, 200

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ CLEAR ALL STUDENTS
# =========================================
def clear_students():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM students")
        conn.commit()
        return {"message": "All students deleted"}, 200

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ GET STUDENT DASHBOARD
# =========================================
def get_student_dashboard(rollno):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        rollno = rollno.strip().lower()

        # 🔹 student
        cur.execute(
            "SELECT rollno, name FROM students WHERE rollno=%s",
            (rollno,)
        )
        student = cur.fetchone()

        if not student:
            return {"error": "Student not found"}, 404

        # 🔹 marks
        cur.execute(
            "SELECT subject, marks FROM marks WHERE rollno=%s",
            (rollno,)
        )
        marks = cur.fetchall()

        # 🔹 attendance
        cur.execute(
            "SELECT date, status FROM attendance WHERE rollno=%s",
            (rollno,)
        )
        attendance = cur.fetchall()

        total = len(attendance)
        present = sum(1 for a in attendance if a["status"] == "present")

        percentage = round((present / total) * 100, 2) if total else 0

        return {
            "student": student,
            "marks": marks,
            "attendance": {
                "total": total,
                "present": present,
                "percentage": percentage
            }
        }, 200

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ ADD MARKS (UPSERT)
# =========================================
def add_marks(rollno, subject, marks, teacher_id=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        rollno = rollno.strip().lower()

        cur.execute(
            """
            INSERT INTO marks (rollno, subject, marks, teacher_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, subject)
            DO UPDATE SET 
                marks = EXCLUDED.marks,
                teacher_id = EXCLUDED.teacher_id
            """,
            (rollno, subject, marks, teacher_id)
        )

        conn.commit()
        return {"message": "Marks saved"}, 200

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ MARK ATTENDANCE
# =========================================
def mark_attendance(rollno, status, teacher_id=None):
    conn = get_connection()
    cur = conn.cursor()

    today = date.today()

    try:
        rollno = rollno.strip().lower()

        cur.execute(
            """
            INSERT INTO attendance (rollno, date, status, teacher_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, date)
            DO UPDATE SET 
                status = EXCLUDED.status,
                teacher_id = EXCLUDED.teacher_id
            """,
            (rollno, today, status.lower(), teacher_id)
        )

        conn.commit()
        return {"message": "Attendance saved"}, 200

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()