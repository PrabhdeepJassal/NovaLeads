# 🚀 NovaLeads — Complete Start Guide

> **Last updated**: June 26, 2026  
> **Author**: TESS  
> **Stack**: Python (XGBoost) + FastAPI + React + PostgreSQL  
> **Formerly known as**: LeadPredict

---

## 📋 PREREQUISITES CHECK

Before starting, make sure you have these installed:

```bash
# Check Python
python3 --version         # Should be 3.10+

# Check PostgreSQL
psql --version            # Should be 16.x ✅ (already installed)

# Check Node
node --version            # Should be 18+
npm --version             # Should be 9+
```

---

## 🗄️ STEP 1 — SET UP POSTGRESQL DATABASE

### Start PostgreSQL (if not running)
```bash
brew services start postgresql@16
```

### Create the database
```bash
# Connect to PostgreSQL
psql postgres

# Create the database (inside psql shell)
CREATE DATABASE novaleads;

# Verify it's created
\l            # You should see "novaleads" in the list

# Exit psql
\q
```

> ✅ **Done!** Your database is ready.

---

## 🐍 STEP 2 — SET UP PYTHON BACKEND

### Navigate to backend
```bash
cd ~/LeadPredict/backend
```

### Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install all dependencies
```bash
pip install -r requirements.txt
```

### Create your `.env` file
```bash
cp .env.example .env
```

Edit `.env` and update ONLY the JWT secret (or keep the default for dev):
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/novaleads
JWT_SECRET=your-random-secret-here-change-in-production
```

### Run database migrations (creates all tables)
```bash
python3 -c "
import asyncio
from api.database import create_tables
asyncio.run(create_tables())
print('✅ Database tables created!')
"
```

### Start the backend server
```bash
uvicorn api.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Verify the API is alive
Open in browser: [http://localhost:8000/health](http://localhost:8000/health)  
You should see: `{    "status": "healthy", "service": "NovaLeads API"}`

### Open API Docs (auto-generated)
Open: [http://localhost:8000/docs](http://localhost:8000/docs)  
This shows all 24 API endpoints with "Try it out" buttons. 🔥

> ✅ **Backend is running!** Keep this terminal open.

---

## ⚛️ STEP 3 — SET UP REACT FRONTEND

Open a **new terminal** (keep backend running in the first one).

```bash
cd ~/LeadPredict/frontend
```

### Install dependencies
```bash
npm install
```

### Start the dev server
```bash
npm run dev
```

You should see:
```
VITE v5.x.x  ready in XXms
➜  Local:   http://localhost:5173/
```

### Open the app
Open: [http://localhost:5173](http://localhost:5173) in your browser.

> ✅ **Frontend is running!**

---

## 🧪 STEP 4 — FIRST TIME SETUP (Create Admin)

### Register an admin user
Using the API docs at [http://localhost:8000/docs](http://localhost:8000/docs):

1. Find `POST /api/auth/register`
2. Click "Try it out"
3. Enter:
```json
{
  "email": "admin@novaleads.com",
  "password": "admin123",
  "name": "Admin",
  "company_name": "NovaLeads",
  "role": "admin"
}
```
4. Click "Execute"

### Login
1. Find `POST /api/auth/login`
2. Try it with:
```json
{
  "email": "admin@leadpredict.com",
  "password": "admin123"
}
```
3. Copy the `access_token` from the response

### Create a test employee
1. Find `POST /api/auth/register` again
2. Enter:
```json
{
  "email": "emp1@test.com",
  "password": "emp123",
  "name": "Rajesh",
  "company_name": "NovaLeads",
  "role": "employee"
}
```

### Register 2-3 more employees the same way
```json
{"email": "emp2@test.com", "password": "emp123", "name": "Priya", "company_name": "LeadPredict", "role": "employee"}
{"email": "emp3@test.com", "password": "emp123", "name": "Aman", "company_name": "LeadPredict", "role": "employee"}
```

> ✅ **Users created!** Now go to the frontend and log in.

---

## 🎮 STEP 5 — USE THE APP

### Login as an Employee
1. Open [http://localhost:5173](http://localhost:5173)
2. Log in with: `emp1@test.com` / `emp123`
3. You'll see the Employee Dashboard

### Create Leads
1. Click **"Add Lead"** button
2. Fill in the form:
   - Company: "Acme Corp"
   - Contact: "Vikram"
   - Source: "Referral"
   - Industry: "Technology"
   - Company Size: 100
3. Submit → The ML model will instantly predict Cold/Rejected/Successful with a % confidence
4. Create a few leads with different sources/industries

### View Predictions
- Each lead row shows its **ML Prediction badge** (colored) with confidence %
- Click a lead → **Detail modal** with:
  - 📊 **Prediction tab**: 3-bar probability chart + Top Factors driving the prediction
  - 📋 **Details tab**: All lead info
  - 📝 **Activity tab**: History log

### Try Different Lead Types
Create leads that mimic different scenarios:

| Scenario | How to Set | Expected Prediction |
|----------|-----------|-------------------|
| **Hot 🔥** | Referral, Tech, size 200, high visits/emails, 4 meetings done, demo yes | **Successful** |
| **Cold ❄️** | Cold Call, Manufacturing, size 10, 0 emails, 0 meetings, no follow-ups | **Cold** |
| **On Fence ✋** | LinkedIn, Finance, some visits, 2 meetings but 0 done, competitor considering | **Rejected** |

### Login as Admin
1. Log out, log in with: `admin@novaleads.com` / `admin123`
2. You'll see the **Admin Dashboard**:
   - 🏆 **Leaderboard** — All employees ranked by conversion rate
   - 📈 **Charts** — Monthly trends, status distribution
   - 🧠 **Model Info** — Model accuracy, feature importance, retrain button

---

## 🧠 UNDERSTANDING THE ML MODEL

### How Predictions Work

```
Lead enters the system
        ↓
18 features extracted (source, engagement, meetings, etc.)
        ↓
XGBoost model processes them
        ↓
3 probabilities: Cold ❄️ / Rejected ✋ / Successful ✅
        ↓
Highest probability = Final Prediction
```

### Features the Model Looks At

| Rank | Feature | Impact |
|------|---------|--------|
| 1 | **meetings_done** 🥇 | Highest signal — leads who attend meetings convert |
| 2 | **meetings_scheduled** | Good signal if they actually show up |
| 3 | **follow_ups_total** | Consistent follow-ups = warmer leads |
| 4 | **calls_made** | Engagement indicator |
| 5 | **emails_clicked** | Interest signal |

### Current Model Performance

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| **Cold ❄️** | 78% | 84% | 81% |
| **Rejected ✋** | 73% | 76% | 74% |
| **Successful ✅** | 85% | 73% | 79% |
| **Overall** | | | **~78% Accuracy** |

---

## 📁 PROJECT MAP

```
NovaLeads/
├── START-HERE.md              ← You are here 📍
├── .env.example               ← Environment template
├── .gitignore
│
├── backend/
│   ├── requirements.txt       ← Python dependencies
│   ├── .env                   ← Your config (create this)
│   │
│   ├── api/                   ← FastAPI Backend
│   │   ├── main.py            ← App entry, CORS, routers
│   │   ├── config.py          ← Settings (env vars)
│   │   ├── database.py        ← SQLAlchemy async engine
│   │   ├── models/            ← DB models (User, Lead, ActivityLog)
│   │   ├── schemas/           ← Pydantic schemas (request/response)
│   │   ├── middleware/        ← JWT auth + role checks
│   │   └── routes/            ← API endpoints (auth, leads, employee, admin, predict)
│   │
│   └── ml/                    ← ML Model (Python)
│       ├── train.py           ← Training pipeline
│       ├── predict.py         ← prediction functions
│       ├── retrain.py         ← Retraining script
│       ├── model_schema.py    ← Pydantic models for ML
│       ├── model.pkl          ← Trained XGBoost (488 KB)
│       ├── preprocessor.pkl   ← Feature pipeline
│       └── data/
│           ├── lead_data.csv  ← 2,500 synthetic samples
│           └── sample_data_generator.py
│
└── frontend/                  ← React + Vite + Tailwind
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx            ← Routes + AuthProvider
        ├── context/           ← Auth context
        ├── services/          ← API calls (auth, leads, admin, predictions)
        ├── components/        ← Reusable UI (Layout, LeadTable, PredictionBadge, etc.)
        └── pages/             ← LoginPage, EmployeeDashboard, AdminDashboard, etc.
```

---

## 🔄 QUICK COMMANDS REFERENCE

```bash
# Start PostgreSQL
brew services start postgresql@16

# Start Backend (Terminal 1)
cd ~/LeadPredict/backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# Start Frontend (Terminal 2)
cd ~/LeadPredict/frontend
npm run dev

# Retrain ML Model (after adding real data)
cd ~/LeadPredict/backend
source venv/bin/activate
python3 -c "from ml.retrain import retrain; retrain('ml/data/lead_data.csv')"

# Check all tables in DB
psql -d leadpredict -c "\dt"
```

---

## 🛠️ WHAT YOU CAN DO NEXT

- [ ] Upload real lead data → retrain model for better accuracy
- [ ] Customize the color scheme in `tailwind.config.js`
- [ ] Add more lead source options in the form
- [ ] Export lead reports as CSV
- [ ] Deploy online when ready (Railway/Render)

---

## ❓ TROUBLESHOOTING

| Problem | Fix |
|---------|-----|
| `psql: could not connect to server` | Run `brew services start postgresql@16` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in venv |
| Frontend can't reach API | Check backend is running on port 8000 |
| `relation "users" does not exist` | Run the database creation command in Step 2 |
| Model returns error | Run `python3 ml/train.py` to retrain |
| Port 8000 in use | Kill process: `lsof -ti:8000 \| xargs kill -9` |
| Port 5173 in use | Kill process: `lsof -ti:5173 \| xargs kill -9` |

---

*Built by TESS Squad | June 2026*
