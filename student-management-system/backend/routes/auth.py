from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from utils.auth_utils import hash_password, verify_password   # ✅ use your utils

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

        if db is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        cursor = db.cursor(dictionary=True)

        # 🔍 CHECK IF USER EXISTS
        cursor.execute("SELECT * FROM users WHERE rollno=%s", (rollno,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "status": "error",
                "message": "User already exists"
            }), 409

        # 🔐 HASH PASSWORD (USING UTILS ✅)
        hashed_password = hash_password(password)

        # ✅ INSERT USER
        cursor.execute(
            "INSERT INTO users (rollno, password) VALUES (%s, %s)",
            (rollno, hashed_password)
        )

        # ✅ INSERT STUDENT
        cursor.execute(
            "INSERT INTO students (rollno, name) VALUES (%s, %s)",
            (rollno, "Student")
        )

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Registered successfully"
        }), 201

    except Exception as e:
        print("REGISTER ERROR:", e)
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

    if not rollno or not password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    db = None
    cursor = None

    try:
        db = get_db_connection()

        if db is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE rollno=%s", (rollno,))
        user = cursor.fetchone()

        # 🔐 VERIFY PASSWORD (USING UTILS ✅)
        if user and verify_password(user["password"], password):
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
        print("LOGIN ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()