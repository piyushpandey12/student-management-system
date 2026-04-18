# ================= IMPORTS =================
import os
import json
from urllib.parse import quote

from flask import Blueprint, redirect, url_for, jsonify, request
from flask_dance.contrib.google import make_google_blueprint, google

from backend.utils.db import get_connection, release_connection
from backend.utils.auth_utils import hash_password, verify_password

# ================= BLUEPRINT =================
auth_bp = Blueprint("auth", __name__)

# =========================================================
# 🔐 GOOGLE OAUTH SETUP
# =========================================================
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="auth.google_callback"
)

# =========================================================
# 🌐 GOOGLE LOGIN
# =========================================================
@auth_bp.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("auth.google_callback"))

# =========================================================
# 🌐 GOOGLE CALLBACK
# =========================================================
@auth_bp.route("/google/callback")
def google_callback():

    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    if not resp.ok:
        return jsonify({"error": "Failed to fetch user"}), 400

    info = resp.json()

    email = info.get("email")
    name = info.get("name")
    photo = info.get("picture")

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "SELECT identifier, role FROM users WHERE identifier=%s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            role = "student"

            cursor.execute("""
                INSERT INTO users (identifier, password, role, email)
                VALUES (%s, %s, %s, %s)
            """, (email, None, role, email))

            cursor.execute("""
                INSERT INTO students (rollno, name, email)
                VALUES (%s, %s, %s)
            """, (email, name, email))

            db.commit()
        else:
            role = user[1]

        user_data = {
            "id": email,
            "name": name,
            "photo": photo,
            "role": role
        }

        return redirect(
            f"{os.getenv('FRONTEND_URL')}/google-success.html?user={quote(json.dumps(user_data))}"
        )

    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 REGISTER
# =========================================================
@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():

    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json() or {}

    identifier = data.get("rollno")   # unified field
    password = data.get("password")
    role = data.get("role", "student")

    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT 1 FROM users WHERE identifier=%s", (identifier,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "User already exists"
            }), 409

        hashed_password = hash_password(password)

        # ✅ INSERT USER
        cursor.execute("""
            INSERT INTO users (identifier, password, role)
            VALUES (%s, %s, %s)
        """, (identifier, hashed_password, role))

        # ✅ CREATE PROFILE
        if role == "student":
            cursor.execute("""
                INSERT INTO students (rollno, name)
                VALUES (%s, %s)
            """, (identifier, "Student"))

        elif role == "teacher":
            cursor.execute("""
                INSERT INTO teachers (teacher_id, name)
                VALUES (%s, %s)
            """, (identifier, "Teacher"))

        db.commit()

        return jsonify({
            "status": "success",
            "message": "Registered successfully",
            "role": role
        }), 201

    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            release_connection(db)   # ✅ FIXED


# =========================================================
# 📌 LOGIN
# =========================================================
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():

    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json() or {}

    identifier = data.get("rollno")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT identifier, password, role 
            FROM users 
            WHERE identifier=%s
        """, (identifier,))

        user = cursor.fetchone()

        if user:
            db_id, db_password, role = user

            # ✅ GOOGLE USER
            if db_password is None:
                return jsonify({
                    "status": "success",
                    "user": {
                        "id": db_id,
                        "role": role
                    }
                }), 200

            # ✅ NORMAL LOGIN
            if verify_password(db_password, password):
                return jsonify({
                    "status": "success",
                    "user": {
                        "id": db_id,
                        "role": role
                    }
                }), 200

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
            release_connection(db)   # ✅ FIXED