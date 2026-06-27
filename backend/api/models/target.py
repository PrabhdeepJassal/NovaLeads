"""
NovaLeads — Performance Target ORM model.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime (naive, for DB compat)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PerformanceTarget(Base):
    """Monthly revenue target for an employee."""

    __tablename__ = "performance_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month = Column(String(7), nullable=False)  # e.g. "2026-06"
    revenue_target = Column(Float, nullable=False, default=100000.0)
    actual_revenue = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # ── Relationships ───────────────────────────────────────────
    employee = relationship("User", back_populates="performance_targets")

    def __repr__(self) -> str:
        return f"<PerformanceTarget {self.month} / emp={self.employee_id}>"
