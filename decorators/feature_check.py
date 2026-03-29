from functools import wraps
from flask import jsonify
from models import *
from flask_jwt_extended import get_jwt_identity

def require_feature(feature_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))

            sub = Subscription.query.filter_by(user_id=user.id).first()
            if not sub:
                return jsonify({"msg": "No subscription"}), 403

            plan = Plan.query.get(sub.plan_id)

            features = (
                db.session.query(Feature.name)
                .join(PlanFeature, Feature.id == PlanFeature.feature_id)
                .filter(PlanFeature.plan_id == plan.id)
                .all()
            )

            feature_names = [f[0] for f in features]

            if feature_name not in feature_names:
                return jsonify({"msg": "Upgrade to access this feature"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator