from flask import Blueprint, request, jsonify
import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

student_bp = Blueprint('student', __name__)

def get_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

@student_bp.route('/students', methods=['GET'])
def get_students():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(students)


@student_bp.route('/students', methods=['POST'])
def add_student():
    data = request.json
    roll_no = data.get("rollno")
    name = data.get("name")
    email = data.get("email")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO students (roll_no, name, email) VALUES (%s, %s, %s)",
        (roll_no, name, email)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"status": "student added"})