"""
NovaLeads — Salary Rule ORM model.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID

from api.database import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime (naive, for DB compat)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SalaryRule(Base):
    """Salary deduction rule based on revenue brackets."""

    __tablename__ = "salary_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    min_revenue = Column(Float, nullable=False)
    max_revenue = Column(Float, nullable=False)
    deduction_percent = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

    def __repr__(self) -> str:
        return f"<SalaryRule {self.name} ({self.deduction_percent}% deduction)>"
