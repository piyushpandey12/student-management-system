from werkzeug.security import generate_password_hash, check_password_hash


# ================= HASH PASSWORD =================
def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


# ================= VERIFY PASSWORD =================
def verify_password(stored_password, provided_password):
    if not stored_password or not provided_password:
        return False
    return check_password_hash(stored_password, provided_password)