from flask import Blueprint, request, jsonify
from utils.db import get_connection   # ✅ use ONE db function
from utils.auth_utils import hash_password, verify_password
import mysql.connector

auth_bp = Blueprint('auth', __name__)


# ================= REGISTER =================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    rollno = data.get("rollno")
    password = data.get("password")

    if not rollno or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    hashed_password = hash_password(password)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # ✅ Insert into users table
        cursor.execute(
            "INSERT INTO users (rollno, password) VALUES (%s, %s)",
            (rollno, hashed_password)
        )

        # ✅ Insert into students table
        cursor.execute(
            "INSERT INTO students (rollno, name) VALUES (%s, %s)",
            (rollno, "New Student")
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "User registered successfully"
        })

    except mysql.connector.IntegrityError:
        return jsonify({
            "status": "error",
            "message": "User already exists"
        }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ================= LOGIN =================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    rollno = data.get("rollno")
    password = data.get("password")

    if not rollno or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        # ✅ Step 1: get user
        cursor.execute("SELECT * FROM users WHERE rollno=%s", (rollno,))
        user = cursor.fetchone()

        # ✅ Step 2: verify password (HASHED)
        if user and verify_password(user["password"], password):

            # ✅ Step 3: get student data
            cursor.execute("SELECT * FROM students WHERE rollno=%s", (rollno,))
            student = cursor.fetchone()

            return jsonify({
                "status": "success",
                "student": student
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
        if conn:
            conn.close()