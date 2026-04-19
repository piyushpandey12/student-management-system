# student_model.py

import psycopg2
import os
from datetime import date


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
# ✅ ADD STUDENT
# =========================================
def add_student(rollno, name):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO students (rollno, name) VALUES (%s, %s)",
            (rollno, name)
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
# ✅ GET STUDENT DETAILS
# =========================================
def get_student(rollno):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT rollno, name FROM students WHERE rollno=%s",
        (rollno,)
    )

    student = cur.fetchone()

    cur.close()
    conn.close()

    if not student:
        return None

    return {
        "rollno": student[0],
        "name": student[1]
    }


# =========================================
# ✅ GET MARKS
# =========================================
def get_marks(rollno):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT subject, marks FROM marks WHERE rollno=%s",
        (rollno,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {"subject": r[0], "marks": r[1]}
        for r in rows
    ]


# =========================================
# ✅ GET ATTENDANCE
# =========================================
def get_attendance(rollno):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT date, status FROM attendance WHERE rollno=%s ORDER BY date",
        (rollno,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "date": str(r[0]),
            "status": r[1]
        }
        for r in rows
    ]


# =========================================
# ✅ FULL DASHBOARD DATA
# =========================================
def get_student_dashboard(rollno):
    student = get_student(rollno)

    if not student:
        return {"error": "Student not found"}

    marks = get_marks(rollno)
    attendance = get_attendance(rollno)

    # 📊 Attendance %
    total = len(attendance)
    present = len([a for a in attendance if a["status"] == "present"])

    percentage = round((present / total) * 100, 2) if total > 0 else 0

    return {
        "student": student,
        "marks": marks,
        "attendance": attendance,
        "attendance_percentage": percentage
    }


# =========================================
# ✅ ADD MARKS
# =========================================
def add_marks(rollno, subject, marks, teacher_id=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO marks (rollno, subject, marks, teacher_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, subject)
            DO UPDATE SET marks = EXCLUDED.marks
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
        cur.execute(
            """
            INSERT INTO attendance (rollno, date, status, teacher_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (rollno, date)
            DO UPDATE SET status = EXCLUDED.status
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
