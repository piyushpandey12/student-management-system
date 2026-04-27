# =========================================================
# 📌 IMPORTS
# =========================================================
from backend.utils.db import get_connection, get_cursor, release_connection
from backend.utils.auth_utils import hash_password
from psycopg2.extras import RealDictCursor


# =========================================================
# 📌 GET ALL STUDENTS
# =========================================================
def get_all_students(page=1, limit=50):
    offset = (page - 1) * limit

    db = get_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)

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

        rows = cursor.fetchall()

        return {"data": rows}, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(db)


# =========================================================
# ➕ CREATE STUDENT (FINAL FIX + PASSWORD VALIDATION)
# =========================================================
def create_student(rollno, name, password):
    conn = None

    try:
        # 🔒 VALIDATION
        if not rollno or not name or not password:
            return {"error": "Missing fields"}, 400

        if len(password) < 6:
            return {"error": "Password must be at least 6 characters"}, 400

        conn = get_connection()
        cur = get_cursor(conn)

        # 🔍 check existing user
        cur.execute("SELECT id FROM users WHERE identifier=%s", (rollno,))
        if cur.fetchone():
            return {"error": "Student already exists"}, 400

        # 🔐 hash password
        hashed = hash_password(password)

        # ✅ insert into users
        cur.execute("""
            INSERT INTO users (identifier, name, password, role)
            VALUES (%s, %s, %s, 'student')
            RETURNING id
        """, (rollno, name, hashed))

        row = cur.fetchone()
        if not row or "id" not in row:
            raise Exception("User creation failed")

        user_id = row["id"]

        # ✅ insert into students
        cur.execute("""
         INSERT INTO students (rollno, name)
          VALUES (%s, %s)
        """, (rollno, name, user_id))

        conn.commit()

        return {
            "message": "Student added successfully",
            "rollno": rollno
        }, 201

    except Exception as e:
        if conn:
            conn.rollback()
        return {"error": str(e)}, 500

    finally:
        if conn:
            release_connection(conn)


# =========================================================
# ❌ DELETE STUDENT
# =========================================================
def remove_student(rollno):
    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM students WHERE rollno=%s", (rollno,))
        db.commit()

        return {"message": "Deleted successfully"}, 200

    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(db)


# =========================================================
# 📊 STUDENT DASHBOARD
# =========================================================
def get_student_dashboard_data(rollno):
    db = get_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    try:
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
            "attendance_percent": attendance_percent
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        release_connection(db)