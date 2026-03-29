from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
from extensions import db, jwt
from models import *
from flask_cors import CORS
from routes.auth import auth_bp
from routes.features import features_bp
from routes.projects import project_bp
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager

JWT_TOKEN_LOCATION = ["headers"]
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
UPLOAD_FOLDER = "uploads"
app = Flask(__name__)
app.config.from_object(Config)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie" 
app.config["JWT_COOKIE_SECURE"] = False          
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

CORS(app, supports_credentials=True)
db.init_app(app)
jwt.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(features_bp, url_prefix='/api')
app.register_blueprint(project_bp, url_prefix='/api')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard1')
def dashboard1():
    return render_template('dashboard1.html')  

@app.route('/dashboard2')
def dashboard2():
    return render_template('dashboard2.html')

@app.route('/dashboard')
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=user_id).first()
    if subscription and subscription.status == "active":
        return render_template('dashboard2.html')  
    else:
        return render_template('dashboard1.html')  
    
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
