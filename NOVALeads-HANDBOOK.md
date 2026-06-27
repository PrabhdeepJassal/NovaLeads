# 🚀 NovaLeads — Complete Project Handbook

> **Version**: 1.0.0  
> **Last Updated**: June 27, 2026  
> **Stack**: Python (XGBoost) + FastAPI + React + PostgreSQL  
> **GitHub**: [https://github.com/PrabhdeepJassal/NovaLeads](https://github.com/PrabhdeepJassal/NovaLeads)

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [ML Model — Deep Dive](#-ml-model--deep-dive)
4. [API Reference](#-api-reference)
5. [Database Schema](#-database-schema)
6. [Frontend Guide](#-frontend-guide)
7. [Salary Deduction System](#-salary-deduction-system)
8. [Revenue Tracking](#-revenue-tracking)
9. [Deployment Guide](#-deployment-guide)
10. [Development Guide](#-development-guide)
11. [Troubleshooting](#-troubleshooting)

---

## 1. 📋 Project Overview

### What is NovaLeads?

NovaLeads is an **AI-powered Lead Conversion Prediction SaaS** that helps sales teams predict which leads will convert. It uses a trained XGBoost machine learning model to classify leads into three outcomes:

| Outcome | Label | Description |
|---|---|---|
| **Cold** ❄️ | Will not convert | Dead lead, no interest |
| **Rejected** ✋ | Said no | Actively declined after follow-ups |
| **Successful** ✅ | Will convert | High probability of becoming a customer |

### Two User Roles

| Role | Access |
|---|---|
| **Employee** 👤 | Their own leads, ML predictions, salary info, revenue logging |
| **Admin** 🏢 | Team leaderboard, all employees' data, salary rules, dashboard analytics |

### Core Features

- 🔮 **ML Predictions** — Real-time lead scoring (Cold/Rejected/Successful) on every lead
- 📊 **Employee Dashboard** — Stats cards, leads table, salary impact card, activity feed
- 🏢 **Admin Dashboard** — Leaderboard, charts, conversion funnel, lead insights, activity feed
- 💰 **Salary Deduction Rules** — Admin-set revenue thresholds with auto deduction %
- 📈 **Revenue Tracking** — Log revenue per lead, auto-updates salary calculations
- 📥 **CSV Export** — Export leads and employee performance data
- 📅 **Date Range Filtering** — Filter dashboard stats by custom date ranges
- 🆔 **Employee IDs** — Auto-generated EMP-001, EMP-002, etc.

---

## 2. 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│                   http://localhost:5173                      │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │  Login   │  │ Employee │  │  Admin   │  │  Profile   │ │
│  │  Page    │  │ Dashboard│  │Dashboard │  │   Page     │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ API calls (axios)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                   http://localhost:8000                      │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │   Auth   │  │  Leads   │  │  Admin   │  │  Salary    │ │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes    │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Employee │  │ Predict  │  │ Activity │                  │
│  │  Routes  │  │  Routes  │  │  Routes  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │XGBoost   │  │   ML     │
│Database  │  │Model     │  │Preprocess│
│          │  │.pkl      │  │or.pkl    │
└──────────┘  └──────────┘  └──────────┘
```

### Tech Stack Details

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18 + TypeScript | UI framework |
| **Build** | Vite 5 | Dev server & bundling |
| **Styling** | Tailwind CSS 3 | Utility-first styling |
| **Charts** | Recharts 2 | Data visualizations |
| **Icons** | Lucide React | Icon library |
| **Routing** | React Router v6 | Client-side routing |
| **HTTP** | Axios 1.x | API calls + interceptors |
| **Backend** | Python 3.12+ | API server |
| **API** | FastAPI 0.138 | Async REST framework |
| **ORM** | SQLAlchemy 2.0 | Async database access |
| **Auth** | python-jose + passlib | JWT tokens + bcrypt |
| **ML** | XGBoost 2.1 | Gradient boosting classifier |
| **ML Data** | scikit-learn 1.5 | Preprocessing, metrics |
| **Database** | PostgreSQL 16 | Primary data store |
| **DB Driver** | asyncpg | Async PostgreSQL driver |

---

## 3. 🧠 ML Model — Deep Dive

### 3.1 Model Overview

| Property | Value |
|---|---|
| **Algorithm** | XGBoost Classifier |
| **Objective** | `multi:softprob` (multi-class probability) |
| **Classes** | 3 — Cold (0), Rejected (1), Successful (2) |
| **Accuracy** | **90.95%** |
| **ROC AUC (OvR)** | 0.9332 |
| **F1 Macro** | 0.9100 |
| **Training Data** | 10,000 synthetic lead records |
| **Features** | 19 raw + 5 engineered = **24 total** |
| **Model File** | `backend/ml/model.pkl` (488 KB) |
| **Training Script** | `backend/ml/train.py` |

### 3.2 Performance by Class

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Cold** ❄️ | 0.8892 | 0.9407 | 0.9142 | 691 |
| **Rejected** ✋ | 0.9218 | 0.8773 | 0.8990 | 679 |
| **Successful** ✅ | 0.9070 | 0.9268 | 0.9168 | 630 |
| **Overall** | **0.9059** | **0.9095** | **0.9100** | **2000** |

### 3.3 Raw Features (19)

These are the inputs that the model receives for every lead:

| Feature | Type | Range | Description |
|---|---|---|---|
| `lead_source` | Categorical | 7 options | Google Ads, Facebook, LinkedIn, Referral, Organic, Cold Call, Email Campaign |
| `industry` | Categorical | 7 options | Technology, Healthcare, Finance, Education, E-commerce, Real Estate, Manufacturing |
| `company_size` | Integer | 1-5000 | Number of employees |
| `website_visits` | Integer | 0-50 | Times lead visited website |
| `emails_opened` | Integer | 0-20 | Emails opened by lead |
| `emails_clicked` | Integer | 0-10 | Links clicked in emails |
| `calls_made` | Integer | 0-15 | Total calls made to lead |
| `calls_connected` | Integer | 0-10 | Calls that connected |
| `call_duration_minutes` | Integer | 0-300 | Total minutes on calls |
| `meetings_scheduled` | Integer | 0-5 | Meetings booked |
| `meetings_done` | Integer | 0-5 | Meetings attended |
| `days_since_first_contact` | Integer | 1-365 | Days since lead entered system |
| `follow_ups_total` | Integer | 0-30 | Total follow-up actions |
| `demo_requested` | Boolean | 0/1 | Lead asked for demo |
| `budget_available` | Boolean | 0/1 | Lead has budget |
| `decision_maker_contacted` | Boolean | 0/1 | Spoke to decision maker |
| `competitor_considering` | Boolean | 0/1 | Looking at competitors |
| `employee_tenure_days` | Integer | 30-1000 | Sales rep experience |
| `employee_prev_conversion_rate` | Float | 0.05-0.60 | Sales rep historical rate |

### 3.4 Engineered Features (5)

These are computed automatically by `predict.py` when making predictions:

| Feature | Formula | Impact |
|---|---|---|
| **meeting_completion_ratio** 🥇 | `meetings_done / max(meetings_scheduled, 1)` | **#1 predictor (28.2%)** |
| `call_connection_rate` | `calls_connected / max(calls_made, 1)` | 2.1% |
| `email_click_rate` | `emails_clicked / max(emails_opened, 1)` | 1.2% |
| `avg_call_duration` | `call_duration_minutes / max(calls_made, 1)` | 0.7% |
| `engagement_score` | Weighted composite of all engagement metrics | 2.4% |

### 3.5 Feature Importance (Top 10)

```
Rank  Feature                          Weight
─────────────────────────────────────────────
  1   meeting_completion_ratio        28.2%  ████████████████████
  2   meetings_scheduled              28.0%  ████████████████████
  3   meetings_done                   25.4%  ██████████████████
  4   engagement_score                 2.4%  ██
  5   emails_opened                    1.7%  █
  6   website_visits                   1.0%  
  7   call_duration_minutes            0.7%  
  8   calls_made                       0.6%  
  9   follow_ups_total                 0.6%  
 10   lead_source_Facebook             0.5%  
```

### 3.6 Training Pipeline

The training script (`backend/ml/train.py`) performs:

1. **Data Loading** — Loads 10,000 records from `lead_data.csv`
2. **Preprocessing**:
   - One-hot encoding for categorical features (lead_source, industry)
   - StandardScaler for numerical features
   - Train/test split (80/20, stratified)
3. **Feature Engineering** — Computes 5 ratio features
4. **Hyperparameter Tuning** — `RandomizedSearchCV` with 400 iterations, 5-fold cross-validation:

```python
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 4, 5, 6, 7],
    'learning_rate': [0.01, 0.03, 0.05, 0.1],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0],
    'min_child_weight': [1, 3, 5],
    'gamma': [0, 0.1, 0.2],
}
```

5. **Best Parameters Found**:
```json
{
    "colsample_bytree": 0.8,
    "learning_rate": 0.05,
    "max_depth": 4,
    "min_child_weight": 3,
    "n_estimators": 100,
    "subsample": 0.8
}
```

6. **Evaluation** — Prints classification report, confusion matrix, ROC AUC, feature importance
7. **Export** — Saves model.pkl, preprocessor.pkl, feature_names.pkl

### 3.7 Prediction API

The `predict.py` module exposes these functions:

```python
predict_single(lead_data: dict) -> dict
```
Returns:
```json
{
    "probabilities": {"cold": 0.04, "rejected": 0.11, "successful": 0.85},
    "predicted_class": "successful",
    "confidence": 0.85,
    "top_factors": [["meeting_completion_ratio", 0.28], ...]
}
```

```python
predict_batch(leads: list[dict]) -> list[dict]
get_feature_importance() -> list[tuple[str, float]]
```

### 3.8 Retraining

Triggered via `POST /api/predict/retrain` (admin only) or manually:

```bash
cd backend && python3 ml/train.py
```

---

## 4. 📡 API Reference

### 4.1 Authentication

All endpoints except register/login require `Authorization: Bearer <token>` header.

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login, returns JWT tokens |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user profile |
| `/api/auth/me` | PATCH | Update profile |

### 4.2 Leads

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/leads/` | GET | JWT | List own leads (paginated, filterable) |
| `/api/leads/` | POST | JWT | Create lead + auto ML prediction |
| `/api/leads/{id}` | GET | JWT | Get lead details |
| `/api/leads/{id}` | PATCH | JWT | Update lead + re-predict |
| `/api/leads/{id}` | DELETE | JWT | Delete lead |
| `/api/leads/{id}/predict` | POST | JWT | Re-trigger ML prediction |
| `/api/leads/{id}/activity` | GET | JWT | Get lead's activity log |

### 4.3 Employee

| Endpoint | Method | Description |
|---|---|---|
| `/api/employee/dashboard` | GET | Employee stats + activity |
| `/api/employee/performance` | GET | Monthly performance breakdown |
| `/api/employee/leads/by-status` | GET | Leads grouped by status |

### 4.4 Admin

| Endpoint | Method | Description |
|---|---|---|
| `/api/admin/dashboard` | GET | Team stats + leaderboard + trend + status distribution |
| `/api/admin/dashboard?start_date=&end_date=` | GET | Filtered by date range |
| `/api/admin/employees` | GET | All employees with stats |
| `/api/admin/employees/{id}` | GET | Employee detail |
| `/api/admin/employees/{id}/leads` | GET | Employee's leads |
| `/api/admin/activity-feed` | GET | Team-wide activity feed |
| `/api/admin/lead-insights` | GET | Source/industry performance, stale leads |
| `/api/admin/export/leads` | GET | Download all leads as CSV |
| `/api/admin/export/employees` | GET | Download employee perf as CSV |

### 4.5 ML Predictions

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/predict/single` | POST | JWT | Predict single lead |
| `/api/predict/batch` | POST | JWT | Batch prediction |
| `/api/predict/model-info` | GET | JWT | Model metadata + feature importance |
| `/api/predict/retrain` | POST | Admin | Retrain ML model |

### 4.6 Salary

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/salary/rules` | GET | Admin | List all deduction rules |
| `/api/salary/rules` | POST | Admin | Create deduction rule |
| `/api/salary/rules/{id}` | PATCH | Admin | Update rule |
| `/api/salary/rules/{id}` | DELETE | Admin | Delete rule |
| `/api/salary/targets` | GET | Admin | All perf targets with employee names |
| `/api/salary/targets/{id}` | PATCH | Admin | Update actual_revenue |
| `/api/salary/my-info` | GET | JWT | Employee's own salary info |
| `/api/salary/my-target` | GET | JWT | Employee's current target |

---

## 5. 🗄️ Database Schema

### 5.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌──────────────────┐
│    users    │       │    leads    │       │  activity_logs   │
├─────────────┤       ├─────────────┤       ├──────────────────┤
│ id (PK)     │◄──────│ employee_id │       │ id (PK)          │
│ email       │       │ id (PK)     │       │ user_id (FK)     │
│ name        │       │ company_name│       │ lead_id (FK)     │
│ password_ha │       │ contact_name│       │ action           │
│ role        │       │ lead_source │       │ details (JSON)   │
│ company_name│       │ industry    │       │ created_at       │
│ is_active   │       │ company_size│       └──────────────────┘
│ emp_id      │       │ website_visi│
│ employee_ten│       │ emails_open │       ┌──────────────────┐
│ prev_convers│       │ emails_click│       │  salary_rules    │
│ created_at  │       │ calls_made  │       ├──────────────────┤
│ updated_at  │       │ calls_conne │       │ id (PK)          │
└─────────────┘       │ call_durati │       │ name             │
       │              │ meetings_sch│       │ min_revenue      │
       │              │ meetings_do │       │ max_revenue      │
       ▼              │ days_since_│       │ deduction_percent│
┌──────────────────┐  │ follow_ups_│       │ is_active        │
│ performance_target│ │ demo_reques│       │ created_at       │
├──────────────────┤  │ budget_avai│       └──────────────────┘
│ id (PK)          │  │ decision_m │
│ employee_id (FK) │  │ competitor_│
│ month            │  │ status     │
│ revenue_target   │  │ notes      │
│ actual_revenue   │  │ revenue    │
│ created_at       │  │ predicted_o│
│ updated_at       │  │ prediction_│
└──────────────────┘  │ predicted_a│
                      │ created_at │
                      │ updated_at │
                      └────────────┘
```

### 5.2 Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'employee',
    company_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    emp_id VARCHAR(20) UNIQUE,
    employee_tenure_days INTEGER DEFAULT 0,
    prev_conversion_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### 5.3 Leads Table

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    lead_source VARCHAR(50) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    company_size INTEGER NOT NULL,
    website_visits INTEGER DEFAULT 0,
    emails_opened INTEGER DEFAULT 0,
    emails_clicked INTEGER DEFAULT 0,
    calls_made INTEGER DEFAULT 0,
    calls_connected INTEGER DEFAULT 0,
    call_duration_minutes INTEGER DEFAULT 0,
    meetings_scheduled INTEGER DEFAULT 0,
    meetings_done INTEGER DEFAULT 0,
    days_since_first_contact INTEGER NOT NULL,
    follow_ups_total INTEGER DEFAULT 0,
    demo_requested BOOLEAN DEFAULT FALSE,
    budget_available BOOLEAN DEFAULT FALSE,
    decision_maker_contacted BOOLEAN DEFAULT FALSE,
    competitor_considering BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'new',
    notes TEXT,
    revenue FLOAT DEFAULT 0.0,
    predicted_outcome VARCHAR(20),
    prediction_confidence FLOAT,
    predicted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### 5.4 Activity Logs Table

```sql
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    details JSON,
    created_at TIMESTAMP NOT NULL
);
```

### 5.5 Salary Rules Table

```sql
CREATE TABLE salary_rules (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    min_revenue FLOAT NOT NULL,
    max_revenue FLOAT NOT NULL,
    deduction_percent FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL
);
```

### 5.6 Performance Targets Table

```sql
CREATE TABLE performance_targets (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES users(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,
    revenue_target FLOAT DEFAULT 100000,
    actual_revenue FLOAT DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

---

## 6. 🖥️ Frontend Guide

### 6.1 Project Structure

```
frontend/
├── index.html                     # Entry HTML
├── package.json                   # Dependencies
├── vite.config.ts                 # Vite config + proxy
├── tailwind.config.js             # Tailwind with custom colors
├── tsconfig.json                  # TypeScript config
│
└── src/
    ├── main.tsx                   # React entry point
    ├── App.tsx                    # Router + AuthProvider
    ├── index.css                  # Tailwind imports
    │
    ├── types/
    │   └── index.ts               # ALL TypeScript interfaces
    │
    ├── context/
    │   └── AuthContext.tsx         # Auth state management
    │
    ├── services/
    │   ├── api.ts                 # Axios instance + interceptors
    │   ├── auth.ts                # Login/register/refresh
    │   ├── leads.ts               # Lead CRUD
    │   ├── admin.ts               # Admin dashboard + salary
    │   ├── employee.ts            # Employee dashboard + salary
    │   └── predictions.ts         # Prediction API
    │
    ├── components/
    │   ├── Layout.tsx             # Sidebar + header shell
    │   ├── ProtectedRoute.tsx     # Auth guard
    │   ├── AdminRoute.tsx         # Admin role guard
    │   ├── LeadTable.tsx          # Full-featured leads table
    │   ├── LeadModal.tsx          # Create/view/edit lead modal
    │   ├── PredictionBadge.tsx    # Colored outcome badge
    │   ├── PredictionChart.tsx    # Probability bar chart
    │   ├── StatCard.tsx           # Reusable stat card
    │   ├── LoadingSpinner.tsx     # Loading state
    │   ├── EmptyState.tsx         # Empty data state
    │   └── ConfirmDialog.tsx      # Confirmation modal
    │
    └── pages/
        ├── LoginPage.tsx          # Login form
        ├── RegisterPage.tsx       # Registration form
        ├── EmployeeDashboard.tsx   # Main employee view
        ├── AdminDashboard.tsx     # Full admin panel (~1000 lines)
        └── ProfilePage.tsx        # Edit profile
```

### 6.2 Key Components

**LeadModal** (`src/components/LeadModal.tsx`)
- 856 lines — Create, View, and Edit lead modes
- Quick activity logging: 📞 Call (with duration input), 📧 Email, 🤝 Meeting, 🎯 Demo, 💰 Budget, 💰 Revenue
- Real-time prediction refresh after activity logging
- 3 tabs in view mode: Details, Prediction, Activity

**LeadTable** (`src/components/LeadTable.tsx`)
- Sortable columns, search, status filter tabs, pagination
- Color-coded prediction badges with confidence %
- Responsive design

**AdminDashboard** (`src/pages/AdminDashboard.tsx`)
- ~1000 lines — the most feature-rich page
- Team stats, leaderboard, salary rules, activity feed, lead insights, conversion funnel
- Date range filtering, CSV export
- Employee drill-down modal

### 6.3 Color Palette

```css
primary-500: #6366F1    /* Indigo - primary actions */
primary-600: #4F46E5    /* Darker indigo - branding */
cold-500:    #EF4444    /* Red - cold leads */
rejected-500:#F59E0B    /* Amber - rejected leads */
successful-500:#10B981  /* Green - successful leads */
```

### 6.4 Route Map

| Route | Page | Access |
|---|---|---|
| `/login` | LoginPage | Public |
| `/register` | RegisterPage | Public |
| `/dashboard` | EmployeeDashboard | Any authenticated |
| `/admin` | AdminDashboard | Admin only |
| `/profile` | ProfilePage | Any authenticated |
| `/` | RootRedirect | Redirects based on role |

---

## 7. 💰 Salary Deduction System

### 7.1 How It Works

Admins define revenue thresholds with corresponding deduction percentages. The system auto-calculates:

1. Each employee has a **monthly revenue target** (default ₹1,00,000)
2. **Actual revenue** is calculated as the sum of all `revenue` fields across all their leads
3. When revenue is logged on a lead (via PATCH), the performance target's `actual_revenue` auto-updates
4. The system finds the matching salary rule based on actual revenue
5. **Deduction %** and **take-home %** are displayed to the employee

### 7.2 Default Rules

| Rule Name | Revenue Range | Deduction | Employee Takes Home |
|---|---|---|---|
| Below 50K | ₹0 – ₹50,000 | **-75%** | **25%** |
| 50K – 1L | ₹50,000 – ₹1,00,000 | **-50%** | **50%** |
| 1L – 2L | ₹1,00,000 – ₹2,00,000 | **-25%** | **75%** |
| Above 2L | ₹2,00,000+ | **0%** | **100%** |

### 7.3 Example Scenarios

```
Employee Rajesh:
  Target Revenue: ₹1,00,000
  Actual Revenue: ₹75,000
  → Rule: 50K – 1L → -50% deduction → 50% take-home

Employee Priya:
  Target Revenue: ₹1,00,000
  Actual Revenue: ₹0
  → Rule: Below 50K → -75% deduction → 25% take-home

Employee Aman:
  Target Revenue: ₹1,00,000
  Actual Revenue: ₹1,80,000
  → Rule: 1L – 2L → -25% deduction → 75% take-home
```

### 7.4 API Flow

```javascript
// Admin creates a rule
POST /api/salary/rules
{ "name": "Below 50K", "min_revenue": 0, "max_revenue": 50000, "deduction_percent": 75 }

// Employee logs revenue on a lead
PATCH /api/leads/{id}
{ "revenue": 75000 }
// → Auto-updates performance_target.actual_revenue

// Employee checks salary impact
GET /api/salary/my-info
// Returns: { target_revenue, actual_revenue, applicable_rule, deduction_percent, take_home_percent }
```

---

## 8. 💵 Revenue Tracking

### 8.1 Flow Overview

```
Employee Dashboard
    │
    ├── Click a lead → LeadModal (view mode)
    │       │
    │       ├── 📞 Call (adds call_duration_minutes)
    │       ├── 📧 Email (increments engagement)
    │       ├── 🤝 Meeting (increments meetings)
    │       ├── 🎯 Demo (sets demo_requested=true)
    │       ├── 💰 Budget (sets budget_available=true)
    │       └── 💰 Revenue ← NEW
    │               │
    │               └── Type amount → hit Log
    │                       │
    │                       ▼
    │               PATCH /api/leads/{id} { revenue: 75000 }
    │                       │
    │                       ▼
    │               1. Lead.revenue updated ✅
    │               2. Performance target actual_revenue recalculated ✅
    │               3. Salary rule matched ✅
    │               4. Take-home % updated ✅
    │
    └── Employee sees updated salary card
```

---

## 9. 🚀 Deployment Guide

### 9.1 Local Development

**Prerequisites:**
- Python 3.12+
- PostgreSQL 16+
- Node.js 18+
- npm 9+

**Step 1: Database**
```bash
brew services start postgresql@16
psql postgres
CREATE DATABASE novaleads;
\q
```

**Step 2: Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your settings
uvicorn api.main:app --reload --port 8000
```

**Step 3: Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Step 4: ML Model (optional - pre-trained included)**
```bash
cd backend
source venv/bin/activate
python3 ml/train.py
```

### 9.2 API Auto-Docs

Once the backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 9.3 Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@novaleads.com` | `admin123` |
| Employee | `emp1@test.com` | `emp123` |

---

## 10. 🛠️ Development Guide

### 10.1 Adding a New Feature

1. **Backend**: Create route in `backend/api/routes/`, add schema in `backend/api/schemas/`, add model in `backend/api/models/`
2. **Register** the router in `backend/api/main.py`
3. **Frontend**: Add types in `frontend/src/types/index.ts`
4. **Add service** function in `frontend/src/services/`
5. **Build UI** in the appropriate page or component

### 10.2 Code Conventions

- **Python**: Async/await throughout, type hints, docstrings
- **TypeScript**: Strict mode, no `any` types (ideally), interfaces for all data shapes
- **CSS**: Tailwind utility classes, existing color palette
- **API**: Always use async SQLAlchemy sessions, JWT auth via `get_current_user` dependency

### 10.3 Adding to the ML Model

1. Add new feature to `sample_data_generator.py`
2. Add column to the `Lead` model in `models/lead.py`
3. Add to schemas (`LeadCreate`, `LeadUpdate`, `LeadResponse`)
4. Add to `PREDICT_TRIGGER_FIELDS` in `routes/leads.py`
5. Add to `_trigger_prediction()` feature dict in `routes/leads.py`
6. Re-run `python3 ml/train.py`

---

## 11. ❓ Troubleshooting

| Problem | Solution |
|---|---|
| `psql: could not connect to server` | `brew services start postgresql@16` |
| `ModuleNotFoundError: No module named '...'` | `pip install -r requirements.txt` in venv |
| `relation "users" does not exist` | Restart backend — tables are auto-created |
| `Port 8000 already in use` | `lsof -ti:8000 \| xargs kill -9` |
| `Port 5173 already in use` | `lsof -ti:5173 \| xargs kill -9` |
| ML model returns error | `python3 ml/train.py` to retrain |
| Frontend can't reach API | Check backend is running on port 8000 |
| Auth error "Authentication required" | Login again (token may have expired) |
| Admin dashboard shows 0 leads | Backend counts by `predicted_outcome` not `status` — create leads with predictions |
| Salary info shows ₹0 actual | Log revenue via PATCH on a lead, or backfill via DB |
| Performance target missing | `INSERT INTO performance_targets ...` (see schema section) |

---

## 📝 Final Notes

NovaLeads was built by **TESS Squad** under the command of **TESS-Core**.

- **ML Model**: 90.95% accuracy, 24 features, XGBoost
- **Backend**: 19+ API endpoints, JWT auth, async PostgreSQL
- **Frontend**: 5 pages, 10+ components, responsive dashboard
- **Business Logic**: Salary deduction engine, revenue tracking, performance targets

---

*"NovaLeads — AI that knows which leads will shine."* ✨
