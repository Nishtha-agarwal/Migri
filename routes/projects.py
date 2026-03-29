from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import *
from extensions import db
from decorators.feature_check import require_feature

project_bp = Blueprint('project', __name__)

@project_bp.route("/projects", methods=["GET"])
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

@project_bp.route('/create_project', methods=['POST'])
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

@project_bp.route("/delete_project/<int:id>", methods=["DELETE"])
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

@project_bp.route("/update_project/<int:id>", methods=["PUT"])
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

