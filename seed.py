from app import app
from extensions import db
from models import *

with app.app_context():
    db.drop_all()
    db.create_all()

    # 🔹 Tenants
    t1 = Tenant(name="Company A")
    t2 = Tenant(name="Company B")
    db.session.add_all([t1, t2])
    db.session.commit()

    # 🔹 Users
    u1 = User(username="abc", password="abc", tenant_id=t1.id, plan="free")
    u2 = User(username="xyz", password="xyz", tenant_id=t2.id, plan="pro")
    db.session.add_all([u1, u2])
    db.session.commit()

    # 🔹 Plans
    free = Plan(name="Free", max_usage=2)
    pro = Plan(name="Pro", max_usage=10)
    db.session.add_all([free, pro])
    db.session.commit()

    # 🔹 Projects (NOW SAFE)
    p1 = Project(name="project1", tenant_id=t1.id, user_id=u1.id)
    p2 = Project(name="project2", tenant_id=t2.id, user_id=u2.id)
    db.session.add_all([p1, p2])
    db.session.commit()

    f1 = Feature(name="create_project")
    f2 = Feature(name="export_data")
    db.session.add_all([f1, f2])
    db.session.commit()

# 🔹 Map Features to Plans
    db.session.add(PlanFeature(plan_id=free.id, feature_id=f1.id))
    db.session.add(PlanFeature(plan_id=pro.id, feature_id=f1.id))
    db.session.add(PlanFeature(plan_id=pro.id, feature_id=f2.id))
    # 🔹 Subscriptions (FIXED)
    sub1 = Subscription(
        user_id=u1.id,
        tenant_id=t1.id,
        plan_id=free.id,
        status="active",
        amount=0,
        proof_file="free_plan"
    )

    sub2 = Subscription(
        user_id=u2.id,
        tenant_id=t2.id,
        plan_id=pro.id,
        status="active",
        amount=500,
        proof_file="receipt.pdf"
    )

    db.session.add_all([sub1, sub2])

    # 🔹 Usage
    usage1 = Usage(tenant_id=t1.id, used_count=1)
    usage2 = Usage(tenant_id=t2.id, used_count=3)
    db.session.add_all([usage1, usage2])

    db.session.commit()

    print("✅ Database Seeded Successfully!")