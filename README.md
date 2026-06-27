# 🚀 NovaLeads — AI-Powered Lead Conversion Prediction

> **Predict which leads will close. Track your team. Automate salary deductions.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://reactjs.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1-FF6600?logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ What is NovaLeads?

NovaLeads is a **full-stack AI SaaS** that helps sales teams predict lead conversion. It uses a trained XGBoost machine learning model (90.95% accuracy) to classify leads into **Cold ❄️**, **Rejected ✋**, or **Successful ✅** — with real-time predictions, team dashboards, salary deduction rules, and revenue tracking.

### 🎯 Who It's For

- **Sales Employees** — Track your leads, see ML predictions, log activities, know your salary impact
- **Sales Managers / Admins** — Monitor team performance, set salary rules, export reports

### 🔥 Key Features

| Feature | Description |
|---|---|
| 🔮 **ML Predictions** | Real-time 3-class lead scoring with confidence % |
| 📊 **Employee Dashboard** | Leads table, stats cards, salary impact, activity logging |
| 🏢 **Admin Dashboard** | Leaderboard, charts, conversion funnel, lead insights |
| 💰 **Salary Deduction Rules** | Admin-set revenue thresholds → auto deduction % |
| 💵 **Revenue Tracking** | Log revenue per lead → auto salary calculation |
| 📥 **CSV Export** | Download leads & employee performance data |
| 📅 **Date Range Filter** | Filter dashboard stats by custom date range |
| 🆔 **Employee IDs** | Auto-generated EMP-001, EMP-002, ... |
| 📝 **Activity Logging** | Log calls, emails, meetings with one click |

---

## 🧠 ML Model Performance

| Metric | Value |
|---|---|
| **Accuracy** | **90.95%** |
| **ROC AUC** | 0.9332 |
| **F1 Macro** | 0.9100 |
| **Cold F1** | 0.9142 |
| **Rejected F1** | 0.8990 |
| **Successful F1** | 0.9168 |
| **Training Data** | 10,000 synthetic records |
| **Features** | 19 raw + 5 engineered = 24 total |

### Top Predictive Features

```
meeting_completion_ratio   28.2%  ████████████████████
meetings_scheduled         28.0%  ████████████████████
meetings_done              25.4%  ██████████████████
engagement_score            2.4%  ██
emails_opened               1.7%  █
```

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + TypeScript + Vite 5 + Tailwind CSS + Recharts |
| **Backend** | Python 3.12+ / FastAPI 0.138 |
| **Database** | PostgreSQL 16 + asyncpg |
| **ML Model** | XGBoost 2.1 + scikit-learn |
| **Auth** | JWT (python-jose) + bcrypt (passlib) |
| **ORM** | SQLAlchemy 2.0 (async) |

---

## 📸 Dashboard Previews

### Employee Dashboard
```
┌──────────────────────────────────────────────────────────┐
│  👋 Welcome back, Rajesh | EMP-002                       │
│                                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │Totals│ │ ❄️   │ │ ✋   │ │ ✅   │ │  📈  │          │
│  │  13  │ │  4   │ │  3   │ │  6   │ │ 46%  │          │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
│                                                          │
│  💰 Salary This Month                                    │
│  Target: ₹1,00,000 | Actual: ₹75,000 | ████████░░ 75%    │
│  Rule: 50K-1L | -50% deduction | Take-home: 50%         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Your Leads                                      │    │
│  │  [Search...]  [All|Active|Cold|Rejected|Success] │    │
│  │  ┌─────────┬────────┬──────┬──────┬───────────┐  │    │
│  │  │Company  │Contact │Source│Status│ Prediction│  │    │
│  │  │Acme Corp│Vikram  │Referr│new   │ ✅ 77%   │  │    │
│  │  │Beta Ltd │Sneha   │Linked│new   │ ✋ 51%   │  │    │
│  │  │Xylo Inc │Arjun   │Cold  │new   │ ❄️ 69%   │  │    │
│  │  └─────────┴────────┴──────┴──────┴───────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Admin Dashboard
```
┌──────────────────────────────────────────────────────────┐
│  Team Overview: 4 Employees | 13 Leads | 6 Converted     │
│                                                          │
│  Leaderboard              │  Monthly Trends (Chart)      │
│  ┌────┬────────┬───┬────┐ │  ████████████████████       │
│  │ #  │  Name  │Lds│ Cnv│ │  ████████████████████       │
│  │ 1  │ Rajesh │13 │ 6  │ │  ████████████████████       │
│  │ 2  │ Priya  │ 0 │ 0  │ │  Jun 2026                   │
│  │ 3  │ Aman   │ 0 │ 0  │ └─────────────────────────────┘
│  └────┴────────┴───┴────┘ │                              │
│                            │  Status Distribution (Pie)  │
│  Activity Feed             │  ● Cold     ● Rejected      │
│  📞 Rajesh called Acme     │  ● Success  ● Pending       │
│  📧 Priya emailed Beta     │                              │
│  ➕ Aman created lead      │  Salary Rules               │
│                            │  ┌──────┬──────┬──────┐     │
│  Lead Insights             │  │Rule  │Range │Deduct│     │
│  Best: Referral (33%)     │  │50K   │0-50K │ 75%  │     │
│  Stale: 3 leads ⚠️        │  │1L    │50-1L │ 50%  │     │
└──────────────────────────────────────────────────────────┘
```

---

## 💰 Salary Deduction System

Admins define revenue thresholds. System auto-calculates deductions.

| Rule Name | Revenue Range | Deduction | Take-home |
|---|---|---|---|
| Below 50K | ₹0 – ₹50,000 | **-75%** | **25%** |
| 50K – 1L | ₹50,000 – ₹1,00,000 | **-50%** | **50%** |
| 1L – 2L | ₹1,00,000 – ₹2,00,000 | **-25%** | **75%** |
| Above 2L | ₹2,00,000+ | **0%** | **100%** |

Revenue logged on leads → auto-updates salary calculation → employee sees real-time impact.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+, PostgreSQL 16+, Node.js 18+

### 1. Database
```bash
brew services start postgresql@16
psql postgres -c "CREATE DATABASE novaleads;"
```

### 2. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn api.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Open in Browser
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### Default Logins
| Role | Email | Password |
|---|---|---|
| Admin | `admin@novaleads.com` | `admin123` |
| Employee | `emp1@test.com` | `emp123` |

---

## 📁 Project Structure

```
NovaLeads/
├── README.md                    ← You are here
├── NOVALeads-HANDBOOK.md        ← Complete documentation
├── START-HERE.md                ← Quick setup guide
├── .env.example                 ← Environment template
│
├── backend/
│   ├── api/
│   │   ├── main.py              ← FastAPI app entry
│   │   ├── config.py            ← Environment config
│   │   ├── database.py          ← Async SQLAlchemy engine
│   │   ├── models/              ← ORM models (6 files)
│   │   ├── schemas/             ← Pydantic schemas (5 files)
│   │   ├── middleware/          ← JWT auth middleware
│   │   └── routes/              ← Route handlers (7 files)
│   │
│   ├── ml/
│   │   ├── train.py             ← ML training pipeline
│   │   ├── predict.py           ← Inference engine
│   │   ├── retrain.py           ← Retraining script
│   │   ├── model.pkl            ← Trained XGBoost (488 KB)
│   │   └── data/                ← Training data (10K records)
│   │
│   ├── requirements.txt         ← Python dependencies
│   └── Dockerfile               ← Container build
│
└── frontend/
    ├── src/
    │   ├── pages/               ← 5 page components
    │   ├── components/          ← 10 reusable components
    │   ├── services/            ← 6 API service modules
    │   ├── context/             ← Auth context
    │   └── types/               ← TypeScript interfaces
    │
    ├── package.json
    └── vite.config.ts
```

---

## 📡 API Endpoints (30+)

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login` | POST | Login |
| `/api/auth/register` | POST | Register |
| `/api/leads/` | GET | List leads |
| `/api/leads/` | POST | Create lead + predict |
| `/api/leads/{id}` | PATCH | Update lead + re-predict |
| `/api/leads/{id}/activity` | GET | Lead activity log |
| `/api/employee/dashboard` | GET | Employee stats |
| `/api/admin/dashboard` | GET | Team dashboard |
| `/api/admin/employees/{id}/leads` | GET | Employee's leads |
| `/api/admin/lead-insights` | GET | Source/industry perf |
| `/api/admin/export/leads` | GET | CSV export |
| `/api/salary/rules` | GET/POST | Manage deduction rules |
| `/api/salary/my-info` | GET | My salary impact |
| `/api/predict/single` | POST | Predict one lead |
| `/api/predict/model-info` | GET | Model metadata |

Full API docs at http://localhost:8000/docs (Swagger UI) when running.

---

## 🧪 Testing the ML Model

```bash
cd backend
source venv/bin/activate
python3 -c "
from ml.predict import predict_single

# A hot lead
result = predict_single({
    'lead_source': 'Referral',
    'industry': 'Technology',
    'company_size': 200,
    # ... all 19 features
})
print(f'Prediction: {result[\"predicted_class\"]} ({result[\"confidence\"]*100:.1f}%)')
"
```

---

## 📖 Full Handbook

For complete documentation covering every aspect of the system:
👉 **[NOVALeads-HANDBOOK.md](NOVALeads-HANDBOOK.md)**

Includes:
- ML model deep dive (architecture, training, all 24 features)
- Complete API reference
- Database schema with SQL
- Salary deduction engine design
- Development guide
- Troubleshooting

---

## 🛠️ Built With

| Tool | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | Async Python API framework |
| [SQLAlchemy](https://sqlalchemy.org) | Async ORM |
| [XGBoost](https://xgboost.readthedocs.io) | Gradient boosting ML |
| [scikit-learn](https://scikit-learn.org) | ML preprocessing & metrics |
| [React](https://reactjs.org) | Frontend UI |
| [Vite](https://vitejs.dev) | Build tool & dev server |
| [Tailwind CSS](https://tailwindcss.com) | Utility-first styling |
| [Recharts](https://recharts.org) | Charts & graphs |
| [PostgreSQL](https://postgresql.org) | Database |

---

## 📄 License

MIT

---

<p align="center">
  Built by <strong>TESS Squad</strong> 🤖<br>
  <em>"AI that knows which leads will shine."</em> ✨
</p>
