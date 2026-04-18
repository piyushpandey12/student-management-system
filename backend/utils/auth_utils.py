from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# 🔐 HASH PASSWORD
# =========================================================
def hash_password(password: str) -> str:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty")

    return generate_password_hash(
        password.strip(),
        method='pbkdf2:sha256',
        salt_length=16
    )


# =========================================================
# 🔐 VERIFY PASSWORD
# =========================================================
def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Handles:
    ✔ Normal login
    ✔ Google login (no password stored)
    """

    # ❌ No stored password (Google user)
    if stored_password is None:
        return False

    if not provided_password:
        return False

    try:
        return check_password_hash(stored_password, provided_password)
    except Exception as e:
        print("Password verification error:", e)
        return False


# =========================================================
# 🔐 OPTIONAL: CHECK GOOGLE USER
# =========================================================
def is_google_user(stored_password: str) -> bool:
    return stored_password is None