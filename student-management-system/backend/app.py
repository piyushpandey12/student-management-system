from flask import Flask
from flask_cors import CORS
import os

from routes.auth import auth_bp
from routes.student import student_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp

app = Flask(__name__)

# ✅ Enable CORS (allow frontend access)
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(student_bp, url_prefix="/students")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(marks_bp, url_prefix="/marks")

# ✅ Health check route (important for Render)
@app.route("/")
def home():
    return {"status": "ok", "message": "Backend running 🚀"}


# ✅ Important for Gunicorn (Render production)
# (No change needed here, just ensure app = Flask(...) is global)

# ✅ Run locally (ONLY for local testing)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)