from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import *

features_bp = Blueprint('features', __name__)

@features_bp.route('/features', methods=['GET'])
@jwt_required()
def get_features():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # 🔹 Get subscription
    subscription = Subscription.query.filter_by(user_id=user.id).first()

    if subscription:
        plan = Plan.query.get(subscription.plan_id)
    else:
        plan = Plan.query.filter_by(name="Free").first()

    if not plan:
        return jsonify({"msg": "Plan not configured"}), 500

    # 🔹 Define features properly (NO .name usage)
    if plan.name == "Free":
        features = ["Create limited projects", "Basic support"]
    else:
        features = ["Unlimited projects", "Priority support", "Advanced analytics"]

    # 🔹 Usage count (REAL SaaS way)
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
