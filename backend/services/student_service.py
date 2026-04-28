# =========================================================
# 📌 IMPORTS
# =========================================================
from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import hash_password
from psycopg2.extras import RealDictCursor


# =========================================================
# 📌 GET ALL STUDENTS
# =========================================================
def get_all_students(page=1, limit=50):
    offset = (page - 1) * limit

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("""
            SELECT s.rollno, s.name,
                   COALESCE(AVG(m.marks), 0) AS avg_marks
            FROM students s
            LEFT JOIN marks m ON s.rollno = m.rollno
            GROUP BY s.rollno, s.name
            ORDER BY s.rollno
            LIMIT %s OFFSET %s
        """, (limit, offset))

        students = cursor.fetchall()

        return {"data": students}, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(conn)


# =========================================================
# ➕ CREATE STUDENT (FINAL FIXED)
# =========================================================
def create_student(name, rollno, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        rollno = rollno.strip().lower()

        # 🔒 VALIDATION
        if not name or not rollno or not password:
            return {"error": "Missing fields"}, 400

        if len(password) < 4:
            return {"error": "Password too short"}, 400

        # 🔍 CHECK EXISTING (IMPORTANT FIX)
        cursor.execute(
            "SELECT 1 FROM students WHERE rollno=%s",
            (rollno,)
        )

        if cursor.fetchone():
            return {"error": "Student already exists"}, 400

        # 🔐 HASH PASSWORD
        hashed = hash_password(password)

        # ✅ INSERT INTO USERS
        cursor.execute("""
            INSERT INTO users (identifier, name, password, role)
            VALUES (%s, %s, %s, 'student')
        """, (rollno, name, hashed))

        # ✅ INSERT INTO STUDENTS
        cursor.execute("""
            INSERT INTO students (rollno, name)
            VALUES (%s, %s)
        """, (rollno, name))

        conn.commit()

        return {
            "message": "Student added successfully"
        }, 201

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(conn)


# =========================================================
# ❌ DELETE STUDENT
# =========================================================
def remove_student(rollno):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        rollno = rollno.strip().lower()

        # 🔍 check exists
        cursor.execute(
            "SELECT 1 FROM students WHERE rollno=%s",
            (rollno,)
        )

        if not cursor.fetchone():
            return {"error": "Student not found"}, 404

        # 🔥 DELETE BOTH TABLES
        cursor.execute("DELETE FROM students WHERE rollno=%s", (rollno,))
        cursor.execute("DELETE FROM users WHERE identifier=%s", (rollno,))

        conn.commit()

        return {"message": "Deleted successfully"}, 200

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(conn)


# =========================================================
# 📊 STUDENT DASHBOARD
# =========================================================
def get_student_dashboard_data(rollno):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        rollno = rollno.strip().lower()

        # 🔎 STUDENT
        cursor.execute(
            "SELECT rollno, name FROM students WHERE rollno=%s",
            (rollno,)
        )
        student = cursor.fetchone()

        if not student:
            return {"error": "Student not found"}, 404

        # 📊 MARKS
        cursor.execute("""
            SELECT subject, marks
            FROM marks
            WHERE rollno=%s
        """, (rollno,))
        marks = cursor.fetchall()

        avg_marks = (
            sum(m["marks"] for m in marks) / len(marks)
            if marks else 0
        )

        # 📅 ATTENDANCE
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status='present') AS present,
                COUNT(*) AS total
            FROM attendance
            WHERE rollno=%s
        """, (rollno,))

        result = cursor.fetchone() or {}

        present = result.get("present", 0)
        total = result.get("total", 0)

        attendance_percent = (
            round((present / total) * 100, 2)
            if total else 0
        )

        return {
            "student": student,
            "marks": marks,
            "average_marks": round(avg_marks, 2),
            "attendance_percent": attendance_percent,
            "present_days": present,
            "total_days": total
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(conn)