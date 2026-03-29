from extensions import db
from datetime import datetime

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    users = db.relationship('User', backref='tenant', lazy=True)
                            
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    
    plan = db.Column(db.String, default="free")
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    projects = db.relationship('Project', backref='user', lazy=True)
    subscription = db.relationship('Subscription', backref='user', uselist=False)

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    max_usage = db.Column(db.Integer)
    features = db.relationship('PlanFeature', backref='plan', lazy=True)
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) 

class PlanFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'))
    feature = db.relationship('Feature')

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    
    status = db.Column(db.String(20)) 
    amount = db.Column(db.Integer)
    proof_file = db.Column(db.String)
    
class Usage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    tenant_id = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)

