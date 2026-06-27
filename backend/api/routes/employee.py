"""
LeadPredict — Employee stats & dashboard routes.

All endpoints are scoped to the currently authenticated user.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.lead import ActivityLog, Lead
from api.models.user import User
from api.middleware.auth import get_current_user
from api.schemas.dashboard import (
    EmployeeDashboard,
    LeadsByStatusItem,
    LeadsByStatusResponse,
    MonthlyTrend,
    PerformanceItem,
    PerformanceResponse,
    RecentActivityItem,
)

router = APIRouter(prefix="/api/employee", tags=["Employee Stats"])


@router.get("/dashboard", response_model=EmployeeDashboard)
async def employee_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeDashboard:
    """Get the employee's personal dashboard summary.

    Returns aggregate counts, conversion rate, monthly trends,
    and the 10 most recent activity log entries.
    """
    # --- Load all leads for this employee ---
    result = await db.execute(
        select(Lead).where(Lead.employee_id == current_user.id)
    )
    leads = result.scalars().all()

    total_leads = len(leads)
    cold_leads = sum(1 for l in leads if l.status == "cold" or l.predicted_outcome == "cold")
    rejected_leads = sum(1 for l in leads if l.status == "rejected" or l.predicted_outcome == "rejected")
    successful_leads = sum(1 for l in leads if l.status == "successful" or l.predicted_outcome == "successful")
    pending_leads = total_leads - cold_leads - rejected_leads - successful_leads
    conversion_rate = successful_leads / total_leads if total_leads > 0 else 0.0

    # --- Monthly trend ---
    trend_map: dict[str, dict] = {}
    for lead in leads:
        month_key = lead.created_at.strftime("%Y-%m")
        entry = trend_map.setdefault(
            month_key,
            {"month": month_key, "total": 0, "cold": 0, "rejected": 0, "successful": 0},
        )
        entry["total"] += 1
        if lead.status == "cold" or lead.predicted_outcome == "cold":
            entry["cold"] += 1
        elif lead.status == "rejected" or lead.predicted_outcome == "rejected":
            entry["rejected"] += 1
        elif lead.status == "successful" or lead.predicted_outcome == "successful":
            entry["successful"] += 1

    monthly_trend = [
        MonthlyTrend(**trend_map[k]) for k in sorted(trend_map.keys())
    ]

    # --- Recent activity ---
    activity_result = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
    )
    activities = activity_result.scalars().all()

    recent_activity = [
        RecentActivityItem(
            id=act.id,
            user_name=current_user.name,
            action=act.action,
            details=act.details,
            created_at=act.created_at,
        )
        for act in activities
    ]

    return EmployeeDashboard(
        total_leads=total_leads,
        cold_leads=cold_leads,
        rejected_leads=rejected_leads,
        successful_leads=successful_leads,
        pending_leads=pending_leads,
        conversion_rate=round(conversion_rate, 4),
        monthly_trend=monthly_trend,
        recent_activity=recent_activity,
    )


@router.get("/performance", response_model=PerformanceResponse)
async def employee_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceResponse:
    """Get monthly performance breakdown (leads created vs converted)."""
    result = await db.execute(
        select(Lead).where(Lead.employee_id == current_user.id)
    )
    leads = result.scalars().all()

    monthly: dict[str, dict] = {}
    for lead in leads:
        month_key = lead.created_at.strftime("%Y-%m")
        entry = monthly.setdefault(
            month_key, {"month": month_key, "created": 0, "converted": 0}
        )
        entry["created"] += 1
        if lead.status == "successful":
            entry["converted"] += 1

    items = []
    for m in sorted(monthly.keys()):
        data = monthly[m]
        cr = data["converted"] / data["created"] if data["created"] > 0 else 0.0
        items.append(
            PerformanceItem(
                month=data["month"],
                leads_created=data["created"],
                leads_converted=data["converted"],
                conversion_rate=round(cr, 4),
            )
        )

    return PerformanceResponse(items=items)


@router.get("/leads/by-status", response_model=LeadsByStatusResponse)
async def employee_leads_by_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadsByStatusResponse:
    """Get leads grouped by status with counts."""
    result = await db.execute(
        select(Lead).where(Lead.employee_id == current_user.id)
    )
    leads = result.scalars().all()

    counts: dict[str, int] = {}
    for lead in leads:
        counts[lead.status] = counts.get(lead.status, 0) + 1

    # Return in a consistent order
    status_order = ("new", "active", "cold", "rejected", "successful")
    items = [
        LeadsByStatusItem(status=s, count=counts[s])
        for s in status_order
        if s in counts
    ]

    return LeadsByStatusResponse(items=items)
