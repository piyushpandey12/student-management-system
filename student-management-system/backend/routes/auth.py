from flask import Blueprint, request, jsonify
from utils.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

# ================= REGISTER =================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    rollno = data.get("rollno")
    password = data.get("password")

    if not rollno or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # 🔥 Save directly in students table
        cursor.execute(
            "INSERT INTO students (rollno, name, password) VALUES (%s, %s, %s)",
            (rollno, "Student", password)
        )

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Registered successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()


# ================= LOGIN =================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    rollno = data.get("rollno")
    password = data.get("password")

    if not rollno or not password:
        return jsonify({"status": "error"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM students WHERE rollno=%s AND password=%s",
            (rollno, password)
        )

        user = cursor.fetchone()

        if user:
            return jsonify({
                "status": "success",
                "student": user
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid credentials"
            }), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()