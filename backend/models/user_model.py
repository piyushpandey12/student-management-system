import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================
# 🔌 DATABASE CONNECTION
# =========================================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "student_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password")
    )


# =========================================
# ✅ REGISTER USER (LOCAL)
# =========================================
def register_user(identifier, name, password, role):
    conn = get_connection()
    cur = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cur.execute("""
            INSERT INTO users (identifier, name, password, role, provider)
            VALUES (%s, %s, %s, %s, 'local')
        """, (identifier, name, hashed_password, role))

        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ GOOGLE AUTH (LOGIN + SIGNUP)
# =========================================
def google_auth_user(identifier, google_id, role):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 🔎 Check existing user
        cur.execute(
            "SELECT id, provider, role FROM users WHERE identifier=%s",
            (identifier,)
        )
        user = cur.fetchone()

        if not user:
            # ✅ CREATE USER
            cur.execute("""
                INSERT INTO users (identifier, role, google_id, provider)
                VALUES (%s, %s, %s, 'google')
                RETURNING id
            """, (identifier, role, google_id))

            user_id = cur.fetchone()[0]
            conn.commit()

            return {
                "success": True,
                "id": user_id,
                "identifier": identifier,
                "role": role
            }

        else:
            user_id, provider, existing_role = user

            # ❗ Prevent wrong login type
            if provider != "google":
                return {"error": "Use password login for this account"}

            # 🔁 Optional: update role if changed
            if existing_role != role:
                cur.execute(
                    "UPDATE users SET role=%s WHERE id=%s",
                    (role, user_id)
                )
                conn.commit()

            return {
                "success": True,
                "id": user_id,
                "identifier": identifier,
                "role": role
            }

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# =========================================
# ✅ GET USER BY IDENTIFIER
# =========================================
def get_user(identifier):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, identifier, password, role, provider
        FROM users WHERE identifier=%s
    """, (identifier,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return None

    return {
        "id": user[0],
        "identifier": user[1],
        "password": user[2],
        "role": user[3],
        "provider": user[4]
    }


# =========================================
# ✅ LOGIN USER (LOCAL)
# =========================================
def login_user(identifier, password):
    user = get_user(identifier)

    if not user:
        return {"error": "User not found"}

    # ❗ Prevent Google users using password login
    if user["provider"] == "google":
        return {"error": "Use Google login"}

    if not check_password_hash(user["password"], password):
        return {"error": "Invalid password"}

    return {
        "success": True,
        "user": {
            "identifier": user["identifier"],
            "role": user["role"]
        }
    }


# =========================================
# ✅ DELETE USER (OPTIONAL)
# =========================================
def delete_user(identifier):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM users WHERE identifier=%s", (identifier,))
        conn.commit()
        return {"success": True}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()