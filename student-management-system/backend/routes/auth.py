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

    # 🔍 VALIDATION
    if not rollno or not password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # 🔍 CHECK IF USER ALREADY EXISTS
        cursor.execute("SELECT * FROM users WHERE rollno=%s", (rollno,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "status": "error",
                "message": "User already exists"
            }), 409

        # 🔐 HASH PASSWORD
        hashed_password = generate_password_hash(password)

        # ✅ INSERT INTO USERS TABLE
        cursor.execute("""
            INSERT INTO users (rollno, password)
            VALUES (%s, %s)
        """, (rollno, hashed_password))

        # ✅ INSERT INTO STUDENTS TABLE
        cursor.execute("""
            INSERT INTO students (rollno, name)
            VALUES (%s, %s)
        """, (rollno, "Student"))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Registered successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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

    # 🔍 VALIDATION
    if not rollno or not password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # 🔍 FETCH USER
        cursor.execute("SELECT * FROM users WHERE rollno=%s", (rollno,))
        user = cursor.fetchone()

        # 🔐 VERIFY PASSWORD
        if user and check_password_hash(user["password"], password):
            return jsonify({
                "status": "success",
                "student": {
                    "rollno": rollno
                }
            }), 200

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid credentials"
            }), 401

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()