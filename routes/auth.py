from flask import Blueprint, request, jsonify
from models import User
from extensions import db
from flask_jwt_extended import create_access_token, set_access_cookies

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    user = User(
        username=data['username'],
        password=data['password'],
        tenant_id=data['tenant_id']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created"})

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

