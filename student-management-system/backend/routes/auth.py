from flask import Blueprint, request, jsonify
from utils.db import get_connection   # ✅ updated
from utils.auth_utils import hash_password, verify_password

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
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()

        if db is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        cursor = db.cursor()

        # 🔍 CHECK IF USER EXISTS
        cursor.execute("SELECT 1 FROM users WHERE rollno=%s", (rollno,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "User already exists"
            }), 409

        # 🔐 HASH PASSWORD
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
        if db:
            db.rollback()   # ✅ important for PostgreSQL
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
        db = get_connection()

        if db is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        cursor = db.cursor()

        cursor.execute(
            "SELECT rollno, password FROM users WHERE rollno=%s",
            (rollno,)
        )

        user = cursor.fetchone()

        # user = (rollno, password)
        if user:
            db_rollno, db_password = user

            if verify_password(db_password, password):
                return jsonify({
                    "status": "success",
                    "student": {
                        "rollno": db_rollno
                    }
                }), 200

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