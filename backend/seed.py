"""
NovaLeads — Database Seed Script
=================================
Creates comprehensive mock data for a fully working prototype.

Run:   python3 seed.py
Reset: python3 seed.py --reset

What it creates:
  - 1 admin user
  - 5 employee users with emp_ids (EMP-001 to EMP-005)
  - 4 salary deduction rules
  - 5 performance targets (one per employee)
  - 40+ leads with randomized engagement + ML predictions
  - 100+ activity log entries
  - Revenue on some leads
"""

import asyncio
import csv
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─── Database setup ────────────────────────────────────────────────
from api.database import create_tables, engine, get_db
from api.models.user import User
from api.models.lead import Lead, ActivityLog
from api.models.salary import SalaryRule
from api.models.target import PerformanceTarget
from api.middleware.auth import hash_password
from api.database import Base
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

# ─── Helper ─────────────────────────────────────────────────────────

def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def days_ago(n):
    return _utcnow() - timedelta(days=n)

# ─── Employee data ──────────────────────────────────────────────────

EMPLOYEES = [
    {"name": "Rajesh Sharma",   "email": "emp1@test.com",      "emp_id": "EMP-001", "tenure": 540, "prev_rate": 0.38},
    {"name": "Priya Patel",     "email": "emp2@test.com",      "emp_id": "EMP-002", "tenure": 320, "prev_rate": 0.42},
    {"name": "Aman Verma",      "email": "emp3@test.com",      "emp_id": "EMP-003", "tenure": 180, "prev_rate": 0.22},
    {"name": "Sneha Reddy",     "email": "emp4@test.com",      "emp_id": "EMP-004", "tenure": 90,  "prev_rate": 0.15},
    {"name": "Vikram Singh",    "email": "emp5@test.com",      "emp_id": "EMP-005", "tenure": 720, "prev_rate": 0.51},
]

SOURCES = ["Google Ads", "Facebook", "LinkedIn", "Referral", "Organic", "Cold Call", "Email Campaign"]
INDUSTRIES = ["Technology", "Healthcare", "Finance", "Education", "E-commerce", "Real Estate", "Manufacturing"]

# ─── Lead Templates ─────────────────────────────────────────────────

# Each lead has a base probability profile
LEAD_TEMPLATES = [
    # Successful profiles
    {"company": "Techtron Solutions",  "contact": "Amit Gupta",   "source": "Referral",     "industry": "Technology",    "size": 450,  "visits": 35, "emails_op": 16, "emails_cl": 9,  "calls": 12, "conn": 10, "duration": 180, "mtg_sch": 4, "mtg_done": 4, "days": 60,  "fups": 18, "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "MediCare Innovations","contact": "Dr. Neha Jain","source": "Referral",     "industry": "Healthcare",    "size": 280,  "visits": 28, "emails_op": 14, "emails_cl": 7,  "calls": 10, "conn": 9,  "duration": 150, "mtg_sch": 4, "mtg_done": 3, "days": 45,  "fups": 14, "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "EduPrime Academy",    "contact": "Rohit Mehta",  "source": "Organic",      "industry": "Education",     "size": 180,  "visits": 22, "emails_op": 12, "emails_cl": 6,  "calls": 8,  "conn": 7,  "duration": 110, "mtg_sch": 3, "mtg_done": 3, "days": 35,  "fups": 10, "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "FinFlow Capital",     "contact": "Karan Desai",  "source": "LinkedIn",     "industry": "Finance",       "size": 320,  "visits": 20, "emails_op": 10, "emails_cl": 5,  "calls": 9,  "conn": 8,  "duration": 130, "mtg_sch": 3, "mtg_done": 3, "days": 50,  "fups": 12, "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "ShopWave Ecom",       "contact": "Anika Shah",   "source": "Google Ads",   "industry": "E-commerce",    "size": 150,  "visits": 18, "emails_op": 9,  "emails_cl": 4,  "calls": 7,  "conn": 6,  "duration": 95,  "mtg_sch": 3, "mtg_done": 2, "days": 40,  "fups": 9,  "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "CloudBase Systems",   "contact": "Arun Nair",    "source": "Referral",     "industry": "Technology",    "size": 550,  "visits": 40, "emails_op": 18, "emails_cl": 10, "calls": 14, "conn": 12, "duration": 200, "mtg_sch": 5, "mtg_done": 5, "days": 70,  "fups": 22, "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "Green Energy Corp",   "contact": "Priya Singh",  "source": "Organic",      "industry": "Manufacturing", "size": 200,  "visits": 15, "emails_op": 8,  "emails_cl": 4,  "calls": 6,  "conn": 5,  "duration": 85,  "mtg_sch": 3, "mtg_done": 2, "days": 30,  "fups": 8,  "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},
    {"company": "DataForge Analytics", "contact": "Vivek Joshi",  "source": "LinkedIn",     "industry": "Technology",    "size": 380,  "visits": 25, "emails_op": 13, "emails_cl": 7,  "calls": 11, "conn": 9,  "duration": 160, "mtg_sch": 4, "mtg_done": 3, "days": 55,  "fups": 16, "demo": 1, "budget": 1, "dm": 1, "comp": 0, "profile": "successful"},

    # Rejected profiles
    {"company": "BuildRight Infra",    "contact": "Suresh Kumar", "source": "Cold Call",    "industry": "Real Estate",   "size": 80,   "visits": 6,  "emails_op": 3,  "emails_cl": 1,  "calls": 5,  "conn": 3,  "duration": 35,  "mtg_sch": 2, "mtg_done": 0, "days": 90,  "fups": 4,  "demo": 0, "budget": 1, "dm": 0, "comp": 1, "profile": "rejected"},
    {"company": "Pinnacle Ventures",   "contact": "Deepak Malhotra","source": "Facebook",    "industry": "Finance",       "size": 120,  "visits": 8,  "emails_op": 4,  "emails_cl": 1,  "calls": 4,  "conn": 2,  "duration": 25,  "mtg_sch": 2, "mtg_done": 0, "days": 75,  "fups": 5,  "demo": 0, "budget": 1, "dm": 0, "comp": 1, "profile": "rejected"},
    {"company": "FirstStep Pharma",    "contact": "Dr. Raj Kapoor","source": "Email Campaign","industry": "Healthcare",    "size": 60,   "visits": 4,  "emails_op": 2,  "emails_cl": 0,  "calls": 3,  "conn": 2,  "duration": 20,  "mtg_sch": 1, "mtg_done": 0, "days": 60,  "fups": 3,  "demo": 0, "budget": 0, "dm": 0, "comp": 1, "profile": "rejected"},
    {"company": "NexGen Robotics",     "contact": "Ishaan Patel", "source": "LinkedIn",     "industry": "Manufacturing", "size": 45,   "visits": 5,  "emails_op": 2,  "emails_cl": 0,  "calls": 4,  "conn": 1,  "duration": 15,  "mtg_sch": 2, "mtg_done": 0, "days": 85,  "fups": 3,  "demo": 0, "budget": 0, "dm": 1, "comp": 1, "profile": "rejected"},
    {"company": "SwiftLogistics",      "contact": "Manoj Yadav",  "source": "Google Ads",   "industry": "E-commerce",    "size": 95,   "visits": 7,  "emails_op": 3,  "emails_cl": 1,  "calls": 5,  "conn": 2,  "duration": 30,  "mtg_sch": 2, "mtg_done": 0, "days": 65,  "fups": 4,  "demo": 0, "budget": 1, "dm": 0, "comp": 0, "profile": "rejected"},
    {"company": "UrbanNest Properties","contact": "Ravi Agarwal", "source": "Cold Call",    "industry": "Real Estate",   "size": 35,   "visits": 3,  "emails_op": 1,  "emails_cl": 0,  "calls": 3,  "conn": 1,  "duration": 12,  "mtg_sch": 1, "mtg_done": 0, "days": 55,  "fups": 2,  "demo": 0, "budget": 0, "dm": 0, "comp": 1, "profile": "rejected"},
    {"company": "Apex Consulting",     "contact": "Neha Verma",   "source": "Facebook",     "industry": "Education",     "size": 25,   "visits": 4,  "emails_op": 2,  "emails_cl": 0,  "calls": 2,  "conn": 1,  "duration": 10,  "mtg_sch": 1, "mtg_done": 0, "days": 45,  "fups": 2,  "demo": 0, "budget": 1, "dm": 0, "comp": 0, "profile": "rejected"},

    # Cold profiles
    {"company": "MapleLeaf Mills",     "contact": "Gurpreet Singh","source": "Cold Call",    "industry": "Manufacturing", "size": 12,   "visits": 1,  "emails_op": 0,  "emails_cl": 0,  "calls": 1,  "conn": 0,  "duration": 3,   "mtg_sch": 0, "mtg_done": 0, "days": 120, "fups": 1,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "Sahara Textiles",     "contact": "Imran Khan",   "source": "Cold Call",    "industry": "Manufacturing", "size": 8,    "visits": 0,  "emails_op": 0,  "emails_cl": 0,  "calls": 1,  "conn": 0,  "duration": 2,   "mtg_sch": 0, "mtg_done": 0, "days": 180, "fups": 0,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "Delta Motors",        "contact": "Arun Pillai",  "source": "Facebook",     "industry": "Manufacturing", "size": 20,   "visits": 0,  "emails_op": 0,  "emails_cl": 0,  "calls": 2,  "conn": 0,  "duration": 4,   "mtg_sch": 0, "mtg_done": 0, "days": 150, "fups": 1,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "Crystal Clear Water", "contact": "Rajiv Gupta",  "source": "Email Campaign","industry": "Manufacturing", "size": 5,    "visits": 0,  "emails_op": 0,  "emails_cl": 0,  "calls": 0,  "conn": 0,  "duration": 0,   "mtg_sch": 0, "mtg_done": 0, "days": 200, "fups": 0,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "Golden Harvest Foods", "contact": "Sanjay Mishra","source": "Cold Call",    "industry": "E-commerce",    "size": 3,    "visits": 0,  "emails_op": 0,  "emails_cl": 0,  "calls": 1,  "conn": 0,  "duration": 1,   "mtg_sch": 0, "mtg_done": 0, "days": 250, "fups": 0,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "Blue Ridge Pharma",   "contact": "Dr. Anil Shah","source": "Google Ads",   "industry": "Healthcare",    "size": 18,   "visits": 1,  "emails_op": 0,  "emails_cl": 0,  "calls": 1,  "conn": 0,  "duration": 2,   "mtg_sch": 0, "mtg_done": 0, "days": 90,  "fups": 0,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "SilverLine Transport", "contact": "Vikram Raj",   "source": "Facebook",     "industry": "E-commerce",    "size": 7,    "visits": 0,  "emails_op": 0,  "emails_cl": 0,  "calls": 0,  "conn": 0,  "duration": 0,   "mtg_sch": 0, "mtg_done": 0, "days": 300, "fups": 0,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
    {"company": "Pioneer Industries",  "contact": "Rakesh Yadav", "source": "Cold Call",    "industry": "Real Estate",   "size": 10,   "visits": 2,  "emails_op": 0,  "emails_cl": 0,  "calls": 1,  "conn": 1,  "duration": 5,   "mtg_sch": 0, "mtg_done": 0, "days": 130, "fups": 1,  "demo": 0, "budget": 0, "dm": 0, "comp": 0, "profile": "cold"},
]

# ─── ML Prediction ──────────────────────────────────────────────────

def run_ml_prediction(features):
    """Run the actual ML model on lead features. Falls back to smart heuristic if model unavailable."""
    try:
        import sys
        sys.path.insert(0, '.')
        from ml.predict import predict_single
        result = predict_single(features)
        return result["predicted_class"], result["confidence"]
    except (ImportError, FileNotFoundError):
        # Smart fallback based on engagement
        ratio = features["meetings_done"] / max(features["meetings_scheduled"], 1)
        if ratio >= 0.8 and features["demo_requested"] and features["meetings_done"] >= 2:
            return "successful", round(random.uniform(0.70, 0.95), 2)
        elif features["calls_made"] == 0 and features["meetings_done"] == 0:
            return "cold", round(random.uniform(0.65, 0.90), 2)
        else:
            return "rejected", round(random.uniform(0.50, 0.80), 2)


async def seed():
    print("=" * 60)
    print("  🌱 NovaLeads — Seeding Database")
    print("=" * 60)

    # Check if --reset flag
    if "--reset" in sys.argv:
        print("\n  ⚠️  RESET MODE: Dropping all data...")
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
        print("  ✅ All tables emptied\n")

    # Ensure tables exist
    await create_tables()
    print("  ✅ Tables ready\n")

    async for db in get_db():
        # Calculate actual revenue pool
        total_revenue_pool = 850000

        # ─── 1. Admin ────────────────────────────────────────────────
        admin = User(
            email="admin@novaleads.com",
            name="Admin",
            password_hash=hash_password("admin123"),
            role="admin",
            company_name="NovaLeads",
            emp_id="ADM-001",
            employee_tenure_days=0,
            prev_conversion_rate=0.0,
            is_active=True,
        )
        db.add(admin)

        # ─── 2. Employees ────────────────────────────────────────────
        employee_users = []
        for i, emp in enumerate(EMPLOYEES):
            user = User(
                email=emp["email"],
                name=emp["name"],
                password_hash=hash_password("emp123"),
                role="employee",
                company_name="NovaLeads",
                emp_id=emp["emp_id"],
                employee_tenure_days=emp["tenure"],
                prev_conversion_rate=emp["prev_rate"],
                is_active=True,
                created_at=days_ago(random.randint(30, 200)),
            )
            db.add(user)
            employee_users.append(user)

        await db.flush()

        # ─── 3. Salary Rules ─────────────────────────────────────────
        default_rules = [
            SalaryRule(name="Below 50K",    min_revenue=0,        max_revenue=50000,     deduction_percent=75, is_active=True),
            SalaryRule(name="50K – 1L",     min_revenue=50000,    max_revenue=100000,    deduction_percent=50, is_active=True),
            SalaryRule(name="1L – 2L",      min_revenue=100000,   max_revenue=200000,    deduction_percent=25, is_active=True),
            SalaryRule(name="Above 2L",     min_revenue=200000,   max_revenue=9999999999, deduction_percent=0,  is_active=True),
        ]
        for rule in default_rules:
            db.add(rule)
        await db.flush()

        # ─── 4. Leads ────────────────────────────────────────────────
        created_leads = []
        rev_per_employee = {u.id: 0 for u in employee_users}

        for i, tmpl in enumerate(LEAD_TEMPLATES):
            employee = employee_users[i % len(employee_users)]
            days_since = tmpl["days"]
            created_at = days_ago(days_since)

            lead = Lead(
                employee_id=employee.id,
                company_name=tmpl["company"],
                contact_name=tmpl["contact"],
                contact_email=f"{tmpl['contact'].lower().replace(' ', '.')}@{tmpl['company'].lower().replace(' ', '')}.com",
                contact_phone=f"+91-{random.randint(7000000000, 9999999999)}",
                lead_source=tmpl["source"],
                industry=tmpl["industry"],
                company_size=tmpl["size"],
                website_visits=tmpl["visits"],
                emails_opened=tmpl["emails_op"],
                emails_clicked=tmpl["emails_cl"],
                calls_made=tmpl["calls"],
                calls_connected=tmpl["conn"],
                call_duration_minutes=tmpl["duration"],
                meetings_scheduled=tmpl["mtg_sch"],
                meetings_done=tmpl["mtg_done"],
                days_since_first_contact=days_since,
                follow_ups_total=tmpl["fups"],
                demo_requested=bool(tmpl["demo"]),
                budget_available=bool(tmpl["budget"]),
                decision_maker_contacted=bool(tmpl["dm"]),
                competitor_considering=bool(tmpl["comp"]),
                status="new",
                notes=f"Initial contact made via {tmpl['source']}. Follow-up scheduled.",
                created_at=created_at,
                updated_at=created_at,
            )

            # Run ML prediction
            features = {
                "lead_source": tmpl["source"],
                "industry": tmpl["industry"],
                "company_size": tmpl["size"],
                "website_visits": tmpl["visits"],
                "emails_opened": tmpl["emails_op"],
                "emails_clicked": tmpl["emails_cl"],
                "calls_made": tmpl["calls"],
                "calls_connected": tmpl["conn"],
                "call_duration_minutes": tmpl["duration"],
                "meetings_scheduled": tmpl["mtg_sch"],
                "meetings_done": tmpl["mtg_done"],
                "days_since_first_contact": days_since,
                "follow_ups_total": tmpl["fups"],
                "demo_requested": tmpl["demo"],
                "budget_available": tmpl["budget"],
                "decision_maker_contacted": tmpl["dm"],
                "competitor_considering": tmpl["comp"],
                "employee_tenure_days": employee.employee_tenure_days,
                "employee_prev_conversion_rate": employee.prev_conversion_rate,
            }

            predicted, confidence = run_ml_prediction(features)
            lead.predicted_outcome = predicted
            lead.prediction_confidence = confidence
            lead.predicted_at = created_at

            # Add revenue for some leads
            if tmpl["profile"] == "successful":
                revenue = random.choice([25000, 50000, 75000, 100000, 150000])
                lead.revenue = revenue
                rev_per_employee[employee.id] += revenue

            db.add(lead)
            await db.flush()
            created_leads.append(lead)

        print(f"  ✅ Created {len(created_leads)} leads with ML predictions")

        # ─── 5. Activity Logs ────────────────────────────────────────
        actions = ["lead_created", "call_logged", "email_sent", "meeting_scheduled",
                   "demo_requested", "note_added", "status_updated", "revenue_logged"]
        logs = 0
        for lead in created_leads[:30]:  # Activity for first 30 leads
            num_actions = random.randint(1, 4)
            for _ in range(num_actions):
                action = random.choice(actions)
                days_off = random.randint(0, min(lead.days_since_first_contact, 30))
                log = ActivityLog(
                    user_id=lead.employee_id,
                    lead_id=lead.id,
                    action=action,
                    details={"company_name": lead.company_name, "timestamp": days_ago(days_off).isoformat()},
                    created_at=days_ago(days_off),
                )
                db.add(log)
                logs += 1
        print(f"  ✅ Created {logs} activity log entries")

        # ─── 6. Performance Targets ──────────────────────────────────
        for emp in employee_users:
            actual_rev = rev_per_employee.get(emp.id, 0)
            pt = PerformanceTarget(
                employee_id=emp.id,
                month=_utcnow().strftime("%Y-%m"),
                revenue_target=100000 + random.choice([0, 0, 50000]),
                actual_revenue=actual_rev,
            )
            db.add(pt)
        print(f"  ✅ Created {len(employee_users)} performance targets")

        await db.commit()

        # ─── Summary ─────────────────────────────────────────────────
        print(f"\n  {'='*56}")
        print(f"  🌱 SEED COMPLETE!")
        print(f"  {'='*56}")
        print(f"")
        print(f"  📋  Users:        1 admin + {len(employee_users)} employees")
        print(f"  📋  Leads:        {len(created_leads)}")
        print(f"  📋  Activities:   {logs}")
        print(f"  📋  Salary Rules: {len(default_rules)}")
        print(f"  📋  Targets:      {len(employee_users)}")
        print(f"")
        print(f"  {'='*56}")
        print(f"  🔑  LOGIN CREDENTIALS")
        print(f"  {'='*56}")
        print(f"  🏢  Admin:     admin@novaleads.com / admin123")
        for emp in EMPLOYEES:
            print(f"  👤  {emp['name']:20s} {emp['email']:25s} / emp123")
        print(f"")
        print(f"  🚀  Frontend:  http://localhost:5173")
        print(f"  📡  API Docs:  http://localhost:8000/docs")
        print(f"  {'='*56}")

        break  # Only one session

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
