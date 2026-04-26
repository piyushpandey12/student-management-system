# =========================================================
# 📌 routes/google_auth.py (FINAL CLEAN VERSION)
# =========================================================

from flask import Blueprint, request, jsonify

from backend.utils.google_auth import verify_google_token
from backend.utils.auth_utils import generate_token
from backend.models.user_model import google_auth_user

google_auth_bp = Blueprint("google_auth", __name__)


# =========================================================
# 🔥 GOOGLE AUTH (LOGIN + SIGNUP)
# =========================================================
@google_auth_bp.route("/google", methods=["POST"])
def google_auth():
    try:
        # ================= INPUT =================
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        token = data.get("token")
        role = data.get("role", "student")

        if not token:
            return jsonify({"error": "Missing Google token"}), 400

        # ================= VERIFY =================
        google_user = verify_google_token(token)

        if not google_user:
            return jsonify({"error": "Invalid Google token"}), 401

        # ================= EXTRACT =================
        identifier = google_user["identifier"]   # email
        email = google_user["email"]
        name = google_user["name"]
        google_id = google_user["google_id"]

        # ================= DB LOGIN / SIGNUP =================
        user = google_auth_user(
            identifier=identifier,
            email=email,
            name=name,
            google_id=google_id,
            role=role
        )

        if not user or "error" in user:
            return jsonify(user or {"error": "Database error"}), 400

        # ================= JWT =================
        jwt_token = generate_token(user["id"], user["role"])

        return jsonify({
            "status": "success",
            "token": jwt_token,
            "user": {
                "identifier": user["identifier"],
                "role": user["role"]
            }
        }), 200

    except Exception as e:
        print("🔥 Google Auth Error:", str(e))

        return jsonify({
            "error": "Google authentication failed",
            "details": str(e)
        }), 500