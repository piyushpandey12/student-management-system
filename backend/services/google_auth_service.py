from models.user_model import User
from utils.google_auth import verify_google_token
from utils.auth_utils import generate_token
from database.db import db

def google_auth_service(google_token, role):
    try:
        payload = verify_google_token(google_token)

        if not payload:
            return {"error": "Invalid Google token"}, 401

        email = payload.get("email")
        google_id = payload.get("sub")   # ✅ MATCHES UTIL NOW

        if not email or not google_id:
            return {"error": "Invalid Google payload"}, 400

        user = User.query.filter_by(identifier=email).first()

        if not user:
            # ✅ CREATE USER (SIGNUP)
            user = User(
                identifier=email,
                role=role,
                provider="google",
                google_id=google_id
            )
            db.session.add(user)
            db.session.commit()

        else:
            # 🔐 SECURITY CHECK
            if user.provider != "google":
                return {"error": "Use password login"}, 400

        # 🔐 GENERATE JWT (RENAMED VARIABLE)
        jwt_token = generate_token(user)

        return {
            "status": "success",
            "token": jwt_token,
            "user": {
                "identifier": user.identifier,
                "role": user.role
            }
        }, 200

    except Exception as e:
        return {
            "error": "Google authentication failed",
            "details": str(e)
        }, 500