from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


# =========================================================
# 📌 REGISTER
# =========================================================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    rollno = data.get("rollno")
    password = data.get("password")

    if not rollno or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # 🔐 HASH PASSWORD
        hashed_password = generate_password_hash(password)

        # ✅ INSERT INTO USERS TABLE
        cursor.execute("""
            INSERT INTO users (rollno, password)
            VALUES (%s, %s)
        """, (rollno, hashed_password))

        # 🔥 ALSO CREATE STUDENT RECORD (IMPORTANT)
        cursor.execute("""
            INSERT INTO students (rollno, name)
            VALUES (%s, %s)
        """, (rollno, "Student"))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Registered successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# =========================================================
# 📌 LOGIN
# =========================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    rollno = data.get("rollno")
    password = data.get("password")

    if not rollno or not password:
        return jsonify({"status": "error"}), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # ✅ GET USER FROM USERS TABLE
        cursor.execute("""
            SELECT * FROM users WHERE rollno=%s
        """, (rollno,))

        user = cursor.fetchone()

        # 🔐 CHECK PASSWORD
        if user and check_password_hash(user["password"], password):

            return jsonify({
                "status": "success",
                "student": {
                    "rollno": rollno
                }
            })

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid credentials"
            }), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()