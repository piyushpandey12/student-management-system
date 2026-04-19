# student_service.py

from backend.utils.db import get_connection, release_connection


# =========================================================
# 📌 GET ALL STUDENTS (PAGINATED)
# =========================================================
def get_all_students(page=1, limit=50):

    offset = (page - 1) * limit

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT rollno, name
            FROM students
            ORDER BY rollno
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cursor.fetchall()

        data = [
            {
                "rollno": r[0],
                "name": r[1]
            }
            for r in rows
        ]

        return {"data": data, "page": page, "limit": limit}, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 📌 ADD STUDENT
# =========================================================
def create_student(rollno, name, password_hash):

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "SELECT add_student(%s, %s, %s)",
            (rollno, name, password_hash)
        )

        db.commit()

        return {"message": "Student added"}, 201

    except Exception as e:
        if db:
            db.rollback()
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 📌 DELETE STUDENT
# =========================================================
def remove_student(rollno):

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT delete_student(%s)", (rollno,))
        db.commit()

        return {"message": "Deleted successfully"}, 200

    except Exception as e:
        if db:
            db.rollback()
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)


# =========================================================
# 📌 STUDENT DASHBOARD (FULL ANALYSIS)
# =========================================================
def get_student_dashboard_data(rollno):

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # 🔎 STUDENT
        cursor.execute(
            "SELECT name FROM students WHERE rollno=%s",
            (rollno,)
        )
        student = cursor.fetchone()

        if not student:
            return {"error": "Student not found"}, 404

        name = student[0]

        # 📊 MARKS
        cursor.execute("""
            SELECT subject, marks
            FROM marks
            WHERE rollno=%s
        """, (rollno,))

        marks_rows = cursor.fetchall()

        marks = [
            {"subject": m[0], "marks": float(m[1])}
            for m in marks_rows
        ]

        avg_marks = (
            sum(m["marks"] for m in marks) / len(marks)
            if marks else 0
        )

        # 📅 ATTENDANCE
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status='present'),
                COUNT(*)
            FROM attendance
            WHERE rollno=%s
        """, (rollno,))

        result = cursor.fetchone()

        present = result[0] or 0
        total = result[1] or 0

        attendance_percent = (
            round((present / total) * 100, 2)
            if total else 0
        )

        # 🔥 PERFORMANCE ANALYSIS
        if avg_marks >= 75:
            performance = "Excellent"
        elif avg_marks >= 50:
            performance = "Average"
        else:
            performance = "Needs Improvement"

        # 🔥 ATTENDANCE ANALYSIS
        if attendance_percent >= 75:
            attendance_status = "Good"
        elif attendance_percent >= 50:
            attendance_status = "Average"
        else:
            attendance_status = "Low"

        return {
            "student": {
                "rollno": rollno,
                "name": name
            },
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

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)