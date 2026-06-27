"""
NovaLeads — FastAPI Application Entry Point.

Assembles the ASGI app with CORS, includes all routers, and manages
the database lifecycle via the lifespan context manager.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.database import async_session_factory, create_tables, engine
from api.routes import admin, auth, employee, leads, predict, salary


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create database tables on startup, seed default data, dispose engine on shutdown."""
    await create_tables()
    await _seed_default_salary_rules()
    yield
    await engine.dispose()


async def _seed_default_salary_rules() -> None:
    """Insert four default salary deduction rules if none exist."""
    from api.models.salary import SalaryRule
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(select(SalaryRule).limit(1))
        if result.scalar_one_or_none() is not None:
            return  # Already seeded

        defaults = [
            SalaryRule(
                name="Below 50K",
                min_revenue=0.0,
                max_revenue=50000.0,
                deduction_percent=75.0,
                is_active=True,
            ),
            SalaryRule(
                name="50K – 1L",
                min_revenue=50000.0,
                max_revenue=100000.0,
                deduction_percent=50.0,
                is_active=True,
            ),
            SalaryRule(
                name="1L – 2L",
                min_revenue=100000.0,
                max_revenue=200000.0,
                deduction_percent=25.0,
                is_active=True,
            ),
            SalaryRule(
                name="Above 2L",
                min_revenue=200000.0,
                max_revenue=9_999_999_999.0,  # effectively infinite
                deduction_percent=0.0,
                is_active=True,
            ),
        ]
        session.add_all(defaults)
        await session.commit()


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(employee.router)
app.include_router(admin.router)
app.include_router(predict.router)
app.include_router(salary.router)


# ---------------------------------------------------------------------------
# Root & health endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["Info"])
async def root() -> dict:
    """Return basic API metadata."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Simple health-check endpoint (always returns 200 when the app is up)."""
    return {"status": "healthy", "service": settings.APP_NAME}
