"""
LeadPredict — Lead CRUD routes.

All lead endpoints are scoped to the currently authenticated employee.
Admins can view any employee's leads via the admin routes.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.lead import ActivityLog, Lead
from api.models.user import User
from api.middleware.auth import get_current_user
from api.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)

router = APIRouter(prefix="/api/leads", tags=["Leads"])

# ---- Fields that should re-trigger ML prediction when changed ----------
PREDICT_TRIGGER_FIELDS = {
    "status",
    "website_visits",
    "emails_opened",
    "emails_clicked",
    "calls_made",
    "calls_connected",
    "meetings_scheduled",
    "meetings_done",
    "follow_ups_total",
    "demo_requested",
    "budget_available",
    "decision_maker_contacted",
    "competitor_considering",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _trigger_prediction(lead: Lead, db: AsyncSession) -> None:
    """Call the ML model to predict outcome for *lead*.

    Silently skips if the model is not available (not trained).
    Populates ``predicted_outcome``, ``prediction_confidence``,
    ``predicted_at`` on the lead object.
    """
    try:
        from ml.predict import predict_single as ml_predict

        # Build feature dict — include user-level attributes the model expects
        features = {
            "lead_source": lead.lead_source,
            "industry": lead.industry,
            "company_size": lead.company_size,
            "website_visits": lead.website_visits,
            "emails_opened": lead.emails_opened,
            "emails_clicked": lead.emails_clicked,
            "calls_made": lead.calls_made,
            "calls_connected": lead.calls_connected,
            "meetings_scheduled": lead.meetings_scheduled,
            "meetings_done": lead.meetings_done,
            "days_since_first_contact": lead.days_since_first_contact,
            "follow_ups_total": lead.follow_ups_total,
            "demo_requested": int(lead.demo_requested),
            "budget_available": int(lead.budget_available),
            "decision_maker_contacted": int(lead.decision_maker_contacted),
            "competitor_considering": int(lead.competitor_considering),
            # User-level features expected by the model
            "employee_tenure_days": lead.employee.employee_tenure_days,
            "employee_prev_conversion_rate": lead.employee.prev_conversion_rate,
        }

        result = ml_predict(features)
        lead.predicted_outcome = result.get("predicted_class")
        lead.prediction_confidence = result.get("confidence")
        lead.predicted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.flush()
    except (ImportError, FileNotFoundError):
        pass  # Model not trained yet — skip silently
    except Exception:
        pass  # Prediction failed — don't block the request


async def _log_activity(
    db: AsyncSession,
    user_id: UUID,
    action: str,
    lead_id: Optional[UUID] = None,
    details: Optional[dict] = None,
) -> None:
    """Persist an activity log entry."""
    log = ActivityLog(
        user_id=user_id,
        lead_id=lead_id,
        action=action,
        details=details or {},
    )
    db.add(log)
    await db.flush()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(
        None, description="Filter by lead status"
    ),
    search: Optional[str] = Query(
        None, min_length=1, description="Search company / contact name or email"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadListResponse:
    """Retrieve the current user's leads with pagination, filtering, and search.

    Results are ordered by most recently created first.
    """
    # Build base query
    query = select(Lead).where(Lead.employee_id == current_user.id)

    if status:
        query = query.where(Lead.status == status)
    if search:
        like_pattern = f"%{search}%"
        query = query.where(
            or_(
                Lead.company_name.ilike(like_pattern),
                Lead.contact_name.ilike(like_pattern),
                Lead.contact_email.ilike(like_pattern),
            )
        )

    # Count total matching records
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Apply pagination
    query = (
        query.order_by(Lead.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    leads = result.scalars().all()

    return LeadListResponse(
        items=[LeadResponse.model_validate(l) for l in leads],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, -(-total // page_size)) if page_size > 0 else 0,
    )


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """Create a new lead and automatically trigger an ML prediction."""
    lead = Lead(employee_id=current_user.id, **data.model_dump())
    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    # Trigger ML prediction (silent if model unavailable)
    await _trigger_prediction(lead, db)

    # Log activity
    await _log_activity(
        db,
        current_user.id,
        "lead_created",
        lead.id,
        {"company_name": lead.company_name, "contact_name": lead.contact_name},
    )

    await db.refresh(lead)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """Get a single lead by ID."""
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id, Lead.employee_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """Update a lead.

    If any prediction-relevant fields change, ML prediction is re-triggered
    automatically.  Status changes are logged separately.
    """
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id, Lead.employee_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    status_changed = "status" in update_data and update_data["status"] != lead.status
    should_predict = any(f in PREDICT_TRIGGER_FIELDS for f in update_data)

    # Apply updates
    for field, value in update_data.items():
        setattr(lead, field, value)

    await db.flush()

    # Re-trigger prediction if needed
    if should_predict:
        await _trigger_prediction(lead, db)

    # Log activity
    if status_changed:
        await _log_activity(
            db,
            current_user.id,
            "status_changed",
            lead.id,
            {"new_status": update_data["status"]},
        )
    else:
        await _log_activity(
            db,
            current_user.id,
            "lead_updated",
            lead.id,
            {"updated_fields": list(update_data.keys())},
        )

    # Update performance target if revenue changed
    if "revenue" in update_data:
        from api.models.target import PerformanceTarget
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        pt_result = await db.execute(
            select(PerformanceTarget).where(
                PerformanceTarget.employee_id == current_user.id,
                PerformanceTarget.month == current_month,
            )
        )
        pt = pt_result.scalar_one_or_none()
        if pt:
            # Recalculate total revenue from all leads
            leads_result = await db.execute(
                select(Lead).where(Lead.employee_id == current_user.id)
            )
            all_leads = leads_result.scalars().all()
            pt.actual_revenue = sum(l.revenue or 0 for l in all_leads)
            await db.flush()

    await db.refresh(lead)
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_200_OK)
async def delete_lead(
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a lead.

    Successful leads cannot be deleted.  Other leads are removed along
    with associated activity logs (via cascade).
    """
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id, Lead.employee_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    if lead.status == "successful":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete a successfully converted lead",
        )

    company_name = lead.company_name
    await db.delete(lead)

    await _log_activity(
        db,
        current_user.id,
        "lead_deleted",
        None,
        {"company_name": company_name},
    )

    return {"success": True, "message": "Lead deleted successfully"}


@router.post("/{lead_id}/predict", response_model=LeadResponse)
async def predict_lead(
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """Manually trigger an ML prediction for a specific lead."""
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id, Lead.employee_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    await _trigger_prediction(lead, db)

    await _log_activity(
        db, current_user.id, "prediction_triggered", lead.id
    )

    await db.refresh(lead)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}/activity")
async def get_lead_activity(
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Get activity log entries for a specific lead."""
    result = await db.execute(
        select(Lead).where(
            Lead.id == lead_id, Lead.employee_id == current_user.id
        )
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    activities = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.lead_id == lead_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
    )
    logs = activities.scalars().all()

    return [
        {
            "id": str(log.id),
            "lead_id": str(log.lead_id) if log.lead_id else None,
            "action": log.action,
            "description": log.details.get("company_name", log.action) if log.details else log.action,
            "user_name": current_user.name,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
