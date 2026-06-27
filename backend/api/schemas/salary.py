"""
NovaLeads — Pydantic schemas for Salary Deduction Rules and Performance Targets.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Salary Rule schemas
# ---------------------------------------------------------------------------


class SalaryRuleCreate(BaseModel):
    """Payload for creating a new salary deduction rule."""

    name: str = Field(..., min_length=1, max_length=100, description="Rule name, e.g. 'Below 50K'")
    min_revenue: float = Field(..., ge=0, description="Minimum revenue for this bracket")
    max_revenue: float = Field(..., ge=0, description="Maximum revenue for this bracket")
    deduction_percent: float = Field(..., ge=0, le=100, description="Deduction percentage (0-100)")
    is_active: bool = True


class SalaryRuleUpdate(BaseModel):
    """Payload for updating an existing salary deduction rule."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    min_revenue: Optional[float] = Field(None, ge=0)
    max_revenue: Optional[float] = Field(None, ge=0)
    deduction_percent: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class SalaryRuleResponse(BaseModel):
    """Schema returned when reading a salary deduction rule."""

    id: UUID
    name: str
    min_revenue: float
    max_revenue: float
    deduction_percent: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Performance Target schemas
# ---------------------------------------------------------------------------


class PerformanceTargetCreate(BaseModel):
    """Payload for creating a performance target (typically auto-created)."""

    employee_id: UUID
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format")
    revenue_target: float = Field(default=100000.0, ge=0)
    actual_revenue: float = Field(default=0.0, ge=0)


class PerformanceTargetUpdate(BaseModel):
    """Payload for updating a performance target."""

    actual_revenue: Optional[float] = Field(None, ge=0)


class PerformanceTargetResponse(BaseModel):
    """Schema returned when reading a performance target."""

    id: UUID
    employee_id: UUID
    month: str
    revenue_target: float
    actual_revenue: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Employee salary info (aggregated view)
# ---------------------------------------------------------------------------


class EmployeeSalaryInfo(BaseModel):
    """Aggregated salary info for the currently authenticated employee."""

    employee_name: str
    emp_id: str
    target_revenue: float
    actual_revenue: float
    applicable_rule: Optional[str] = None
    deduction_percent: float = 0.0
    take_home_percent: float = 100.0
