from flask import Blueprint, request, jsonify
from models import User
from extensions import db
from flask_jwt_extended import create_access_token, set_access_cookies
from sqlalchemy.exc import IntegrityError
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    # 🔹 Step 1: Pre-check
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "Username already exists ❌"}), 400
    # 🔹 Step 2: Create user
    new_user = User(
        username=username,
        password=password,
        plan="free",
        tenant_id=1
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User registered successfully ✅"})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "Username already exists ❌"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Server error ❌", "error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or user.password != data["password"]:
        return jsonify({"msg": "Bad credentials"}), 401
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "tenant_id": user.tenant_id   
        }
    )
    response = jsonify({"msg": "login successful"})
    set_access_cookies(response, access_token)   
    return response
