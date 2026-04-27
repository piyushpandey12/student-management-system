# student_service.py

from backend.utils.db import get_connection, release_connection
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
            SELECT rollno, name
            FROM students
            ORDER BY rollno
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cursor.fetchall()

        return {
            "data": rows,
            "page": page,
            "limit": limit
        }, 200

    except Exception:
        return {"error": "Failed to fetch students"}, 500

    finally:
        cursor.close()
        release_connection(db)


# =========================================================
# 📌 ADD STUDENT (USING DB FUNCTION)
# =========================================================
def create_student(rollno, name, password):

    db = get_connection()
    cursor = db.cursor()

    try:
        # 🔒 basic validation
        if not rollno or not name or not password:
            return {"error": "Invalid input"}, 400

        cursor.execute(
            "SELECT add_student(%s, %s, %s)",
            (rollno, name, password)   # ✅ pass plain password
        )

        db.commit()

        return {"message": "Student added"}, 201

    except Exception:
        db.rollback()
        return {"error": "Failed to add student"}, 500

    finally:
        cursor.close()
        release_connection(db)


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
def remove_student(rollno):

    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT delete_student(%s)", (rollno,))
        db.commit()

        return {"message": "Deleted successfully"}, 200

    except Exception:
        db.rollback()
        return {"error": "Failed to delete student"}, 500

    finally:
        cursor.close()
        release_connection(db)


# =========================================================
# 📌 STUDENT DASHBOARD
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

        result = cursor.fetchone()

        present = result["present"] or 0
        total = result["total"] or 0

        attendance_percent = (
            round((present / total) * 100, 2)
            if total else 0
        )

        # 🔥 ANALYSIS
        performance = (
            "Excellent" if avg_marks >= 75 else
            "Average" if avg_marks >= 50 else
            "Needs Improvement"
        )

        attendance_status = (
            "Good" if attendance_percent >= 75 else
            "Average" if attendance_percent >= 50 else
            "Low"
        )

        return {
            "student": student,
            "marks": marks,
            "average_marks": round(avg_marks, 2),
            "attendance": {
                "percent": attendance_percent,
                "present": present,
                "total": total,
                "status": attendance_status
            },
            "performance": performance
        }, 200

    except Exception:
        return {"error": "Failed to load dashboard"}, 500

    finally:
        cursor.close()
        release_connection(db)