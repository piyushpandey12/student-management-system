# ================= IMPORTS =================
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# 🔐 HASH PASSWORD
# =========================================================
def hash_password(password: str) -> str:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty")

    password = password.strip()

    # 🔒 Strength check
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    return generate_password_hash(
        password,
        method="pbkdf2:sha256",
        salt_length=16
    )


# =========================================================
# 🔐 VERIFY PASSWORD
# =========================================================
def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Handles:
    ✔ Normal login
    ✔ Google users (no password)
    """

    # ❌ No stored password (Google users)
    if stored_password is None or stored_password == "":
        return False

    # ❌ Invalid input
    if not provided_password or not provided_password.strip():
        return False

    try:
        return check_password_hash(
            stored_password,
            provided_password.strip()
        )
    except Exception:
        return False


# =========================================================
# 🔐 CHECK GOOGLE USER
# =========================================================
def is_google_user(stored_password: str) -> bool:
    """
    Google users have empty password ("")
    """
    return stored_password is None or stored_password == ""


# =========================================================
# 🔐 VALIDATE PASSWORD INPUT
# =========================================================
def validate_password(password: str) -> tuple:
    """
    Returns (is_valid, message)
    """

    if not password or not password.strip():
        return False, "Password cannot be empty"

    password = password.strip()

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if password.isdigit():
        return False, "Password cannot be only numbers"

    # 🔥 Optional stronger validation
    if not any(c.isalpha() for c in password):
        return False, "Password must include letters"

    return True, "Valid password"