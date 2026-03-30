# 🚀 SaaS Subscription & Feature Entitlement API

A **Flask-based multi-tenant SaaS backend system** that provides secure and scalable **subscription management with feature-level access control**. This project is designed to simulate real-world SaaS platforms where users belong to different tenants, subscribe to plans, and access features based on entitlements.

## 📌 Overview
This system enables:
* 🏢 **Multi-tenancy** (isolated tenant environments)
* 🔐 **JWT-based authentication**
* 🎭 **Role-based access control**
* 💳 **Subscription plan management**
* ⚙️ **Feature entitlement enforcement**

It is built with clean architecture principles and is suitable for **production-ready SaaS systems**.

## ✨ Core Features

### 🏢 Multi-Tenant Architecture
* Each user belongs to a tenant
* Data isolation across tenants

### 🔐 Authentication & Authorization
* JWT-based authentication
* Secure login & protected routes

### 🎭 Role-Based Access Control
* Roles such as **Admin** and **User**
* Restricted endpoints for admins only

### 💳 Subscription Plans
* Free, Pro, Enterprise plans
* Each plan defines allowed features

### ⚙️ Feature Entitlements
* Feature-level access control
* Middleware-style validation for protected APIs

### 🌱 Database Seeding
* Pre-configured tenants, users, and roles
* Quick project setup using seed script

## 🛠️ Tech Stack
| Layer          | Technology                                    |
| -------------- | --------------------------------------------- |
| Backend        | Flask                                         |
| ORM            | Flask-SQLAlchemy                              |
| Migrations     | Flask-Migrate                                 |
| Authentication | Flask-JWT-Extended                            |
| Serialization  | Marshmallow                                   |
| Database       | SQLite (Development), PostgreSQL (Production) |
| Language       | Python 3.11+                                  |

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
git clone https://github.com/Nishtha-agarwal/Migri
cd Migri

### 2️⃣ Create Virtual Environment
python -m venv venv
# Activate:
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

### 3️⃣ Install Dependencies
pip install -r requirements.txt

## 🌱 Database Seeding
Populate the database with default data:
python seed.py

This will create:
* Default tenants
* Roles (Admin/User)
* Sample users
* Subscription plan

## ▶️ Running the Application
python app.py

📍 Access API at:
`http://127.0.0.1:8000/`


## 🔌 API Endpoints

### 🔑 Authentication

#### Register User
POST /api/register
#### Login
POST /api/login

Returns JWT token for authenticated access.

### 🧩 Feature Access
#### Protected Feature Endpoint
GET /api/features/dashboard

Requires:
* Valid JWT
* Active subscription
* Feature entitlement

#### Create Subscription Plan
POST /api/subscriptions

## 📡 Example API Calls

### 1️⃣ Register User
curl -X POST http://127.0.0.1:8000 \
-H "Content-Type: application/json" \
-d '{"username":"abc","password":"abc","tenant_id":1}'
-d '{"username":"xyz","password":"zyx","tenant_id":2}'

### 2️⃣ Login (Get JWT)
curl -X POST http://127.0.0.1:8000 \
-H "Content-Type: application/json" \
-d '{"username":"abc","password":"abc"}'
-d '{"username":"xyz","password":"xyz"}'

## 🗂️ Project Structure
saas-subscription-api/
│
├── app.py                 # Main application entry
├── config.py              # Configuration settings
├── models.py              # Database models
│
├── routes/
│   ├── auth.py            # Authentication routes
│   ├── tenants.py         # Tenant management
│   └── features.py        # Feature access APIs
│
├── seed.py                # Database seeding script
├── requirements.txt       # Dependencies
├── migrations/            # DB migrations
└── README.md              # Documentation

## 🏗️ System Architecture
Client (Postman / Frontend)
          ↓
Flask REST API (JWT Auth + RBAC)
          ↓
Business Logic (Feature Entitlement)
          ↓
Database (SQLite / PostgreSQL)

## ⚠️ Challenges & Solutions
| Challenge              | Solution                            |
| ---------------------- | ----------------------------------- |
| Multi-tenant isolation | Tenant ID-based filtering           |
| Secure authentication  | JWT tokens with protected routes    |
| Feature control        | Middleware-based entitlement checks |
| Scalability            | Modular route structure             |

## 📈 Future Enhancements
* Payment gateway integration (Stripe / Razorpay)
* API rate limiting
* Tenant-specific analytics dashboard
* Role hierarchy improvements

## 🎓 Learning Outcomes
* Built a **production-grade SaaS backend**
* Implemented **multi-tenant architecture**
* Applied **JWT authentication & RBAC**
* Designed **scalable API structure**
* Gained experience with **database migrations & seeding**

## 👨‍💻 Author
**Nishtha Agarwal**

## 🌐 Deployment(Render)
🔗 **Live URL:** https://migri-3.onrender.com/
