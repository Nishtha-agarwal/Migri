SaaS Subscription & Feature Entitlement API

A Flask-based multi-tenant SaaS subscription system with feature-level access control. This project supports:

Tenant isolation
Role-based access
Subscription plans
Feature entitlements
JWT authentication

Features
Multi-tenant support
Subscription plan management (Free, Pro, Enterprise)
Feature-based access control
JWT-based authentication
Seed scripts for initial roles, users, and tenants
Swagger or Postman-ready API examples

Tech Stack
Backend: Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended
Database: SQLite (dev) / PostgreSQL (prod)
Authentication: JWT
Others: Python 3.11+, Marshmallow for serialization

Setup Instructions

1. Clone the repository
git clone <your-repo-url>
cd saas-subscription-api

2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

3. Install dependencies
pip install -r requirements.txt

4. Set environment variables (example)
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY='supersecretkey'
export JWT_SECRET_KEY='jwtsecretkey'

5. Initialize the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

Database Seeding
Seed the database with default tenants, roles, and users:
python seed.py

Running the Server
flask run
Access the API at: http://127.0.0.1:8000/

Example API Calls

1. Register a user
curl -X POST http://127.0.0.1:8000/api/register \
-H "Content-Type: application/json" \
-d '{"username":"john", "password":"password123", "tenant_id":1}'

2. Login to get JWT
curl -X POST http://127.0.0.1:8000/api/login \
-H "Content-Type: application/json" \
-d '{"username":"john", "password":"password123"}'

3. Access a feature-protected endpoint
curl -X GET http://127.0.0.1:8000/api/features/dashboard \
-H "Authorization: Bearer <JWT_TOKEN>"

4. Add a subscription plan (Admin only)
curl -X POST http://127.0.0.1:8000/api/subscriptions \
-H "Authorization: Bearer <JWT_TOKEN>" \
-H "Content-Type: application/json" \
-d '{"name":"Pro Plan", "features":["analytics","export"]}

Project Structure:

saas-subscription-api/
│
├── app.py
├── config.py
├── models.py
├── schemas.py
├── routes/
│   ├── auth.py
│   ├── tenants.py
│   ├── subscriptions.py
│   └── features.py
├── seed.py
├── requirements.txt
├── migrations/
└── README.md'