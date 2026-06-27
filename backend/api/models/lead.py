"""
LeadPredict — Lead and ActivityLog ORM models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from api.database import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime (naive, for DB compat)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Lead(Base):
    """A single sales lead tracked by an employee."""

    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Contact Info ────────────────────────────────────────────
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)

    # ── Lead Attributes ─────────────────────────────────────────
    lead_source = Column(String(50), nullable=False)
    industry = Column(String(50), nullable=False)
    company_size = Column(Integer, nullable=False)

    # ── Engagement Metrics ──────────────────────────────────────
    website_visits = Column(Integer, default=0, nullable=False)
    emails_opened = Column(Integer, default=0, nullable=False)
    emails_clicked = Column(Integer, default=0, nullable=False)
    calls_made = Column(Integer, default=0, nullable=False)
    calls_connected = Column(Integer, default=0, nullable=False)
    call_duration_minutes = Column(Integer, default=0, nullable=False)
    meetings_scheduled = Column(Integer, default=0, nullable=False)
    meetings_done = Column(Integer, default=0, nullable=False)
    days_since_first_contact = Column(Integer, nullable=False)
    follow_ups_total = Column(Integer, default=0, nullable=False)

    # ── Flags ───────────────────────────────────────────────────
    demo_requested = Column(Boolean, default=False, nullable=False)
    budget_available = Column(Boolean, default=False, nullable=False)
    decision_maker_contacted = Column(Boolean, default=False, nullable=False)
    competitor_considering = Column(Boolean, default=False, nullable=False)

    # ── Status & Notes ──────────────────────────────────────────
    status = Column(String(20), nullable=False, default="new")
    notes = Column(Text, nullable=True)
    revenue = Column(Float, default=0.0, nullable=False)

    # ── ML Prediction ───────────────────────────────────────────
    predicted_outcome = Column(String(20), nullable=True)
    prediction_confidence = Column(Float, nullable=True)
    predicted_at = Column(DateTime, nullable=True)

    # ── Timestamps ──────────────────────────────────────────────
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # ── Relationships ───────────────────────────────────────────
    employee = relationship("User", back_populates="leads")

    def __repr__(self) -> str:
        return f"<Lead {self.company_name} ({self.status})>"


class ActivityLog(Base):
    """Audit trail for user actions across the platform."""

    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
    )

    action = Column(String(50), nullable=False)
    details = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # ── Relationships ───────────────────────────────────────────
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self) -> str:
        return f"<ActivityLog {self.action} by {self.user_id}>"
