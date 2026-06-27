"""
LeadPredict — Pydantic schemas for dashboard and stats responses.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Employee Dashboard
# ---------------------------------------------------------------------------


class MonthlyTrend(BaseModel):
    """Lead counts for a single month."""

    month: str
    total: int
    cold: int
    rejected: int
    successful: int


class RecentActivityItem(BaseModel):
    """A single activity log entry for the dashboard feed."""

    id: UUID
    user_name: str
    action: str
    details: Optional[dict] = None
    created_at: datetime


class EmployeeDashboard(BaseModel):
    """Employee's personal dashboard summary."""

    total_leads: int
    cold_leads: int
    rejected_leads: int
    successful_leads: int
    pending_leads: int
    conversion_rate: float
    monthly_trend: list[MonthlyTrend]
    recent_activity: list[RecentActivityItem]


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


class PerformanceItem(BaseModel):
    """Monthly performance breakdown for an employee."""

    month: str
    leads_created: int
    leads_converted: int
    conversion_rate: float


class PerformanceResponse(BaseModel):
    """List of performance items."""

    items: list[PerformanceItem]


# ---------------------------------------------------------------------------
# Leads by Status
# ---------------------------------------------------------------------------


class LeadsByStatusItem(BaseModel):
    """Count of leads for a single status."""

    status: str
    count: int


class LeadsByStatusResponse(BaseModel):
    """List of status-count pairs."""

    items: list[LeadsByStatusItem]


# ---------------------------------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------------------------------


class LeaderboardEntry(BaseModel):
    """Employee ranking entry for the admin leaderboard."""

    employee_id: UUID
    name: str
    converted: int
    rate: float
    leads: int


class StatusDistribution(BaseModel):
    """Lead counts across all status categories."""

    cold: int
    rejected: int
    successful: int
    pending: int


class AdminDashboard(BaseModel):
    """Admin overview dashboard."""

    total_employees: int
    total_leads: int
    total_converted: int
    team_conversion_rate: float
    leaderboard: list[LeaderboardEntry]
    monthly_trend: list[MonthlyTrend]
    status_distribution: StatusDistribution
    model_accuracy: float


# ---------------------------------------------------------------------------
# Admin Employee Management
# ---------------------------------------------------------------------------


class AdminEmployeeListItem(BaseModel):
    """Employee summary shown in the admin employee list."""

    id: UUID
    emp_id: Optional[str] = None
    name: str
    email: str
    total_leads: int
    converted_leads: int
    conversion_rate: float
    is_active: bool


class AdminEmployeeListResponse(BaseModel):
    """Paginated (or plain) list of employees."""

    items: list[AdminEmployeeListItem]
    total: int


class AdminEmployeeDetail(BaseModel):
    """Detailed view of a single employee including all their leads."""

    id: UUID
    name: str
    email: str
    role: str
    company_name: str
    is_active: bool
    employee_tenure_days: int
    prev_conversion_rate: float
    total_leads: int
    leads: list[Any]  # Serialised LeadResponse dicts at runtime
    created_at: datetime
    updated_at: datetime
