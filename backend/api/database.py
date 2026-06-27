"""
LeadPredict — Async SQLAlchemy engine, session factory, and Base.

Uses asyncpg for PostgreSQL connectivity with SQLAlchemy 2.x async mode.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from api.config import settings

# ---------------------------------------------------------------------------
# Engine & Session Factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    The session is automatically committed on success or rolled back on
    exception.  The connection is returned to the pool when the request ends.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Table creation helper (used during app startup)
# ---------------------------------------------------------------------------


async def create_tables() -> None:
    """Create all tables defined in ``Base.metadata``.

    This is safe to call on every startup — SQLAlchemy's ``create_all``
    uses ``IF NOT EXISTS`` internally.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
