# routes/google_auth.py

from flask import Blueprint, request, jsonify

from utils.google_auth import verify_google_token
from models.user_model import google_auth_user
from utils.auth_utils import generate_token

google_auth_bp = Blueprint("google_auth", __name__)


@google_auth_bp.route("/google", methods=["POST"])
def google_auth():
    try:
        # ✅ Safe JSON handling
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        token = data.get("token")
        role = data.get("role")

        # 🔐 Validate input
        if not token or not role:
            return jsonify({"error": "Missing token or role"}), 400

        # 🔎 Verify Google token
        payload = verify_google_token(token)

        if not payload:
            return jsonify({"error": "Invalid Google token"}), 401

        # ✅ Extract fields
        email = payload.get("email")
        google_id = payload.get("sub")   # ✔ correct key

        if not email or not google_id:
            return jsonify({"error": "Invalid Google payload"}), 400

        # ✅ DB LOGIN / SIGNUP (UNIFIED)
        result = google_auth_user(email, google_id, role)

        if "error" in result:
            return jsonify(result), 400

        # 🔐 Generate JWT
        jwt_token = generate_token(result["id"], result["role"])

        return jsonify({
            "status": "success",
            "token": jwt_token,
            "user": {
                "identifier": result["identifier"],
                "role": result["role"]
            }
        }), 200

    except Exception as e:
        print("🔥 Google Auth Error:", e)

        return jsonify({
            "error": "Google authentication failed",
            "details": str(e)
        }), 500