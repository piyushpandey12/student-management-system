from flask import Blueprint, request, jsonify
import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

def get_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    roll_no = data.get("rollno")
    password = data.get("password")

    if not roll_no or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    hashed_password = generate_password_hash(password)

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (roll_no, password) VALUES (%s, %s)",
            (roll_no, hashed_password)
        )
        db.commit()
        return jsonify({"status": "registered"})
    except mysql.connector.Error:
        return jsonify({"status": "user exists"}), 400
    finally:
        cursor.close()
        db.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    roll_no = data.get("rollno")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE roll_no=%s", (roll_no,))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"}), 401