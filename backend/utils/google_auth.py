# =========================================================
# 🌐 GOOGLE AUTH UTILS (FINAL)
# =========================================================

from google.oauth2 import id_token
from google.auth.transport import requests
import os

# 🔐 Prefer env (Render), fallback for local dev
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or "891518537612-l1frt7eo83cv9kaq03u1nv561j2jd003.apps.googleusercontent.com"


def verify_google_token(token: str):
    """
    Verify Google ID token and return normalized user payload:
    {
        "identifier": email,
        "email": email,
        "name": name,
        "google_id": sub
    }
    """

    if not token:
        print("❌ No Google token provided")
        return None

    try:
        # 🔎 Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # 🔒 Validate issuer
        if idinfo.get("iss") not in (
            "accounts.google.com",
            "https://accounts.google.com",
        ):
            raise ValueError("Invalid issuer")

        # 🔒 Validate audience (extra safety)
        if GOOGLE_CLIENT_ID and idinfo.get("aud") != GOOGLE_CLIENT_ID:
            raise ValueError("Invalid audience")

        email = idinfo.get("email")
        sub = idinfo.get("sub")   # Google unique user ID
        name = idinfo.get("name") or ""

        # 🔒 Required fields
        if not email or not sub:
            raise ValueError("Missing required Google fields")

        # 📦 Normalized payload (used by routes)
        return {
            "identifier": email,  # ✅ use email as login ID
            "email": email,
            "name": name,
            "google_id": sub      # ✅ store Google unique ID
        }

    except Exception as e:
        print("❌ Google token verification failed:", str(e))
        return None