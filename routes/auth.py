from flask import Blueprint, request, jsonify, Flask
from models import User
from extensions import db
from flask_jwt_extended import create_access_token, set_access_cookies, generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
auth_bp = Blueprint('auth', __name__)
# ---------------- REGISTER ----------------
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("tenant_id")  # 🔹 typo fix in actual code: tenant_id separate
    tenant_id = data.get("tenant_id")

    if not username or not data.get("password") or not tenant_id:
        return jsonify({"error": "All fields are required"}), 400

    if username in users_db:
        return jsonify({"error": "Username already exists"}), 400

    password_hash = generate_password_hash(data.get("password"))
    users_db[username] = {"password_hash": password_hash, "tenant_id": tenant_id}

    return jsonify({"msg": "Registration successful"}), 201

# ---------------- LOGIN ----------------
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_db.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Set session
    session["username"] = username
    session["tenant_id"] = user["tenant_id"]

    return jsonify({"msg": "Login successful"}), 200

# ---------------- DASHBOARD ----------------
@auth_bp.route("/dashboard")
def dashboard():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "msg": f"Welcome {session['username']}!",
        "tenant_id": session["tenant_id"]
    })

# ---------------- LOGOUT ----------------
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"msg": "Logged out"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
