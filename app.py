from flask import Flask, render_template, request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import models
from models import db, User, Tenant, Plan, Project, Feature, PlanFeature, Subscription, Usage
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from seed import run_seed
from flask_login import LoginManager
from flask_jwt_extended import get_jwt_identity, create_access_token, JWTManager, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from flask_jwt_extended import set_access_cookies, jwt_required, unset_jwt_cookies

JWT_TOKEN_LOCATION = ["headers"]
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie" 
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True   # Render = HTTPS
app.config["JWT_COOKIE_SAMESITE"] = "None"        
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
CORS(app, supports_credentials=True)
app.config.from_object(Config)
jwt = JWTManager(app)
db.init_app(app)
with app.app_context():
    db.drop_all() 
    db.create_all()
    run_seed()
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "All fields required"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        tenant = Tenant(name=f"{username}_tenant")
        hashed_pw = generate_password_hash(password)
        new_user = User(
            username=username,
            password=hashed_pw,
            tenant=tenant   # 🔥 use relationship instead of tenant_id
        )
        db.session.add_all([tenant, new_user])
        db.session.commit()
        return jsonify({"msg": "Registration successful"}), 200
    except Exception as e:
        db.session.rollback()
        print("ERROR:", str(e))   # 👈 CHECK THIS IN RENDER LOGS
        return jsonify({"error": "Server error"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
        print("LOGIN DATA:", data)  # 👈 debug
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 401
        if not check_password_hash(user.password, password):
            return jsonify({"error": "Wrong password"}), 401
        access_token = create_access_token(identity=user.id)
        response = jsonify({"msg": "Login successful"})
        set_access_cookies(response, access_token)
        return response
    except Exception as e:
        print("🔥 LOGIN ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify(access_token=new_access_token)

# Logout
@app.route("/api/logout", methods=["POST"])
def logout():
    resp = jsonify({"msg": "Logged out"})
    unset_jwt_cookies(resp)
    return resp, 200

@app.route('/dashboard')
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    subscription = Subscription.query.filter_by(user_id=user_id).first()
    if user.plan == "Pro" and subscription and subscription.status == "active":
        return render_template('dashboard2.html')  
    else:
        return render_template('dashboard1.html')

@app.route('/dashboard1')
def dashboard1():
    return render_template('dashboard1.html')  
    
@app.route('/dashboard2')
def dashboard2():
    return render_template('dashboard2.html') 

@app.route('/api/features', methods=['GET'])
@jwt_required()
def get_features():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"msg": "User not found"}), 404
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    if subscription:
        plan = Plan.query.get(subscription.plan_id)
    else:
        plan = Plan.query.filter_by(name="Free").first()
    if not plan:
        return jsonify({"msg": "Plan not configured"}), 500
    if plan.name == "Free":
        features = ["Create limited projects", "Basic support"]
    else:
        features = ["Unlimited projects", "Priority support", "Advanced analytics"]
    project_count = Project.query.filter_by(user_id=user.id).count()
    return jsonify({
    "plan": {
        "name": plan.name,
        "max_usage": plan.max_usage
    },
    "features": features,
    "usage": {
        "used": project_count,
        "limit": plan.max_usage
    },
    "subscription": {
        "id": subscription.id if subscription else None,
        "status": subscription.status if subscription else "free"
    }
})

@app.route("/api/projects", methods=["GET"])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    projects = Project.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name
        } for p in projects
    ])

@app.route('/api/create_project', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    sub = Subscription.query.filter_by(user_id=user.id).first()
    if sub:
        plan = Plan.query.get(sub.plan_id)
    else:
        plan = Plan.query.filter_by(name="Free").first()
    if not plan:
        return jsonify({"msg": "Plan not found"}), 500
    project_count = Project.query.filter_by(user_id=user.id).count()
    if project_count >= plan.max_usage:
        return jsonify({"msg": "Limit reached"}), 403
    data = request.get_json()
    new_project = Project(
        name=data["name"],
        user_id=user.id,
        tenant_id=user.tenant_id
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"msg": "Project created"})

@app.route("/api/delete_project/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_project(id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    project = Project.query.filter_by(id=id, user_id=user_id).first()
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"msg": "Project deleted"})

@app.route("/api/update_project/<int:id>", methods=["PUT"])
@jwt_required()
def update_project(id):
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    project = Project.query.filter_by(id=id, user_id=user_id).first()
    if not project:
        return jsonify({"msg": "Not found"}), 404
    project.name = data["name"]
    db.session.commit()
    return jsonify({"msg": "Updated"})

@app.route('/api/usage', methods=['GET'])
@jwt_required()
def get_usage():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    usage = Usage.query.filter_by(tenant_id=user.tenant_id).first()
    sub = Subscription.query.filter_by(user_id=user.id).first()
    plan = Plan.query.get(sub.plan_id)
    if usage and usage.used_count >= plan.max_usage:
        return jsonify({"msg": "Usage limit exceeded"}), 403
    return jsonify({"used": usage.used_count if usage else 0})

@app.route('/api/upgrade', methods=['POST'])
@jwt_required()
def upgrade():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    pro_plan = Plan.query.filter_by(name="Pro").first()
    if not pro_plan:
        return jsonify({"error": "Pro plan not found"}), 404
    sub = Subscription.query.filter_by(user_id=user.id).first()
    if not sub:
        return jsonify({"error": "Subscription not found"}), 404
    sub.plan_id = pro_plan.id
    sub.status = "active"
    db.session.commit()
    return jsonify({"msg": "Upgraded to PRO 🚀"})

@app.route('/api/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"msg": "User not found"}), 404
    file = request.files.get('file')
    amount = request.form.get('amount')
    if not file:
        return jsonify({"msg": "No file uploaded"}), 400
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    pro_plan = Plan.query.filter_by(name="Pro").first()
    if not pro_plan:
        return jsonify({"msg": "Pro plan not found"}), 500
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    if subscription:
        subscription.status = "active"
        subscription.amount = amount
        subscription.proof_file = filename
        subscription.plan_id = pro_plan.id
    else:
        new_sub = Subscription(
            user_id=user.id,
            tenant_id=user.tenant_id,
            plan_id=pro_plan.id,
            status="active",
            amount=amount,
            proof_file=filename
        )
        db.session.add(new_sub)
    db.session.commit()
    return jsonify({
        "msg": "Subscription successful! Upgraded to PRO 🚀"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

