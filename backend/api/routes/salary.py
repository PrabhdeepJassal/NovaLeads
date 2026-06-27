"""
NovaLeads — Salary Deduction Rules and Performance Target routes.

Provides admin CRUD for salary rules and performance targets, plus
employee-facing endpoints for viewing personal salary/target info.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.database import get_db
from api.models.salary import SalaryRule
from api.models.target import PerformanceTarget
from api.models.user import User
from api.middleware.auth import admin_only, get_current_user
from api.schemas.salary import (
    EmployeeSalaryInfo,
    PerformanceTargetResponse,
    PerformanceTargetUpdate,
    SalaryRuleCreate,
    SalaryRuleResponse,
    SalaryRuleUpdate,
)

router = APIRouter(prefix="/api/salary", tags=["Salary & Targets"])


# ===========================================================================
# Admin-only routes — Salary Rules
# ===========================================================================


@router.get(
    "/rules",
    response_model=list[SalaryRuleResponse],
)
async def list_rules(
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> list[SalaryRuleResponse]:
    """List all salary deduction rules (ordered by min_revenue)."""
    result = await db.execute(
        select(SalaryRule).order_by(SalaryRule.min_revenue)
    )
    rules = result.scalars().all()
    return [SalaryRuleResponse.model_validate(r) for r in rules]


@router.post(
    "/rules",
    response_model=SalaryRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rule(
    data: SalaryRuleCreate,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> SalaryRuleResponse:
    """Create a new salary deduction rule."""
    rule = SalaryRule(
        name=data.name,
        min_revenue=data.min_revenue,
        max_revenue=data.max_revenue,
        deduction_percent=data.deduction_percent,
        is_active=data.is_active,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return SalaryRuleResponse.model_validate(rule)


@router.patch(
    "/rules/{rule_id}",
    response_model=SalaryRuleResponse,
)
async def update_rule(
    rule_id: UUID,
    data: SalaryRuleUpdate,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> SalaryRuleResponse:
    """Update an existing salary deduction rule."""
    result = await db.execute(select(SalaryRule).where(SalaryRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary rule not found",
        )

    if data.name is not None:
        rule.name = data.name
    if data.min_revenue is not None:
        rule.min_revenue = data.min_revenue
    if data.max_revenue is not None:
        rule.max_revenue = data.max_revenue
    if data.deduction_percent is not None:
        rule.deduction_percent = data.deduction_percent
    if data.is_active is not None:
        rule.is_active = data.is_active

    await db.flush()
    await db.refresh(rule)
    return SalaryRuleResponse.model_validate(rule)


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rule(
    rule_id: UUID,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a salary deduction rule."""
    result = await db.execute(select(SalaryRule).where(SalaryRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary rule not found",
        )

    await db.delete(rule)
    await db.flush()


# ===========================================================================
# Admin-only routes — Performance Targets
# ===========================================================================


@router.get(
    "/targets",
    response_model=list[dict],
)
async def list_targets(
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """List all performance targets with employee names."""
    result = await db.execute(
        select(PerformanceTarget)
        .options(joinedload(PerformanceTarget.employee))
        .order_by(PerformanceTarget.month.desc(), PerformanceTarget.employee_id)
    )
    targets = result.scalars().all()

    items = []
    for t in targets:
        items.append(
            {
                "id": t.id,
                "employee_id": t.employee_id,
                "employee_name": t.employee.name if t.employee else "Unknown",
                "month": t.month,
                "revenue_target": t.revenue_target,
                "actual_revenue": t.actual_revenue,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
        )
    return items


@router.patch(
    "/targets/{target_id}",
    response_model=PerformanceTargetResponse,
)
async def update_target(
    target_id: UUID,
    data: PerformanceTargetUpdate,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> PerformanceTargetResponse:
    """Update actual_revenue for a performance target."""
    result = await db.execute(
        select(PerformanceTarget).where(PerformanceTarget.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance target not found",
        )

    if data.actual_revenue is not None:
        target.actual_revenue = data.actual_revenue

    await db.flush()
    await db.refresh(target)
    return PerformanceTargetResponse.model_validate(target)


# ===========================================================================
# Employee routes
# ===========================================================================


def _get_current_month() -> str:
    """Return the current month as 'YYYY-MM'."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m")


@router.get(
    "/my-info",
    response_model=EmployeeSalaryInfo,
)
async def my_salary_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeSalaryInfo:
    """Get the current employee's salary info for the current month.

    Returns the month's target, actual revenue, the matching salary rule
    (if any), deduction percentage, and take-home percentage.
    """
    month = _get_current_month()

    # Fetch the employee's target for this month
    target_result = await db.execute(
        select(PerformanceTarget).where(
            PerformanceTarget.employee_id == current_user.id,
            PerformanceTarget.month == month,
        )
    )
    target = target_result.scalar_one_or_none()

    target_revenue = target.revenue_target if target else 100000.0
    actual_revenue = target.actual_revenue if target else 0.0

    # Determine the applicable salary rule
    deduction_percent = 0.0
    applicable_rule: str | None = None

    rules_result = await db.execute(
        select(SalaryRule)
        .where(SalaryRule.is_active.is_(True))
        .order_by(SalaryRule.min_revenue)
    )
    rules = rules_result.scalars().all()

    for rule in rules:
        if rule.min_revenue <= actual_revenue < rule.max_revenue:
            deduction_percent = rule.deduction_percent
            applicable_rule = rule.name
            break
    else:
        # If no rule matched (e.g. revenue >= max of last rule),
        # use the last rule's deduction if applicable
        if rules and actual_revenue >= rules[-1].min_revenue:
            last_rule = rules[-1]
            # Only apply the last rule if revenue falls within its range
            if actual_revenue >= last_rule.min_revenue and (
                last_rule.max_revenue == float("inf")
                or actual_revenue < last_rule.max_revenue
            ):
                deduction_percent = last_rule.deduction_percent
                applicable_rule = last_rule.name

    return EmployeeSalaryInfo(
        employee_name=current_user.name,
        emp_id=current_user.emp_id or "",
        target_revenue=target_revenue,
        actual_revenue=actual_revenue,
        applicable_rule=applicable_rule,
        deduction_percent=deduction_percent,
        take_home_percent=100.0 - deduction_percent,
    )


@router.get(
    "/my-target",
    response_model=PerformanceTargetResponse | dict,
)
async def my_current_target(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceTargetResponse | dict:
    """Get the current employee's performance target for the current month."""
    month = _get_current_month()

    result = await db.execute(
        select(PerformanceTarget).where(
            PerformanceTarget.employee_id == current_user.id,
            PerformanceTarget.month == month,
        )
    )
    target = result.scalar_one_or_none()

    if not target:
        return {"detail": "No target set for this month", "month": month}

    return PerformanceTargetResponse.model_validate(target)
