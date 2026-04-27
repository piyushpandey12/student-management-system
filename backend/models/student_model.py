# student_model.py

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
# ✅ GET STUDENT DASHBOARD (OPTIMIZED)
# =========================================
def get_student_dashboard(rollno):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 🔹 Get student
        cur.execute(
            "SELECT rollno, name FROM students WHERE rollno=%s",
            (rollno,)
        )
        student = cur.fetchone()

        if not student:
            return {"error": "Student not found"}

        # 🔹 Get marks
        cur.execute(
            "SELECT subject, marks FROM marks WHERE rollno=%s",
            (rollno,)
        )
        marks = cur.fetchall()

        # 🔹 Get attendance
        cur.execute(
            "SELECT date, status FROM attendance WHERE rollno=%s ORDER BY date",
            (rollno,)
        )
        attendance = cur.fetchall()

        # 📊 Attendance %
        total = len(attendance)
        present = sum(1 for a in attendance if a["status"] == "present")

        percentage = round((present / total) * 100, 2) if total > 0 else 0

        return {
            "student": student,
            "marks": marks,
            "attendance": attendance,
            "attendance_percentage": percentage
        }

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ ADD MARKS (SAFE UPSERT)
# =========================================
def add_marks(rollno, subject, marks, teacher_id=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 🔹 Check student exists
        cur.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if not cur.fetchone():
            return {"error": "Student not found"}

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
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

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
        # 🔹 Validate student
        cur.execute("SELECT 1 FROM students WHERE rollno=%s", (rollno,))
        if not cur.fetchone():
            return {"error": "Student not found"}

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
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()