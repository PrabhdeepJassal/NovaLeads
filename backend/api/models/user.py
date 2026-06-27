"""
LeadPredict — User ORM model.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime (naive, for DB compat)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """Sales employee or admin."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    emp_id = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="employee")  # "employee" | "admin"
    company_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    employee_tenure_days = Column(Integer, default=0, nullable=False)
    prev_conversion_rate = Column(Float, default=0.0, nullable=False)

    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # ── Relationships ───────────────────────────────────────────
    leads = relationship(
        "Lead",
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    performance_targets = relationship(
        "PerformanceTarget",
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
