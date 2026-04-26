# utils/google_auth.py

from google.oauth2 import id_token
from google.auth.transport import requests
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or "891518537612-l1frt7eo83cv9kaq03u1nv561j2jd003.apps.googleusercontent.com"


def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        return {
            "email": idinfo.get("email"),
            "sub": idinfo.get("sub"),
            "name": idinfo.get("name")
        }

    except Exception as e:
        print("❌ Google token verification failed:", e)
        return None