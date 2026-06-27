"""
LeadPredict — Pydantic schemas for Lead CRUD operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Lead Source & Industry constants (shared validation)
# ---------------------------------------------------------------------------

LEAD_SOURCES = (
    "Google Ads",
    "Facebook",
    "LinkedIn",
    "Referral",
    "Organic",
    "Cold Call",
    "Email Campaign",
)
INDUSTRIES = (
    "Technology",
    "Healthcare",
    "Finance",
    "Education",
    "E-commerce",
    "Real Estate",
    "Manufacturing",
)
STATUSES = ("new", "active", "cold", "rejected", "successful")


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""

    company_name: str = Field(..., min_length=1, max_length=255)
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=50)

    lead_source: str = Field(..., pattern=f"^({'|'.join(LEAD_SOURCES)})$")
    industry: str = Field(..., pattern=f"^({'|'.join(INDUSTRIES)})$")
    company_size: int = Field(..., ge=1)

    website_visits: int = Field(default=0, ge=0)
    emails_opened: int = Field(default=0, ge=0)
    emails_clicked: int = Field(default=0, ge=0)
    calls_made: int = Field(default=0, ge=0)
    calls_connected: int = Field(default=0, ge=0)
    call_duration_minutes: int = Field(default=0, ge=0)
    meetings_scheduled: int = Field(default=0, ge=0)
    meetings_done: int = Field(default=0, ge=0)
    days_since_first_contact: int = Field(..., ge=0)
    follow_ups_total: int = Field(default=0, ge=0)

    demo_requested: bool = False
    budget_available: bool = False
    decision_maker_contacted: bool = False
    competitor_considering: bool = False

    notes: Optional[str] = None
    revenue: float = 0.0


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead (all fields optional)."""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)

    lead_source: Optional[str] = Field(
        None, pattern=f"^({'|'.join(LEAD_SOURCES)})$"
    )
    industry: Optional[str] = Field(
        None, pattern=f"^({'|'.join(INDUSTRIES)})$"
    )
    company_size: Optional[int] = Field(None, ge=1)

    website_visits: Optional[int] = Field(None, ge=0)
    emails_opened: Optional[int] = Field(None, ge=0)
    emails_clicked: Optional[int] = Field(None, ge=0)
    calls_made: Optional[int] = Field(None, ge=0)
    calls_connected: Optional[int] = Field(None, ge=0)
    call_duration_minutes: Optional[int] = Field(None, ge=0)
    meetings_scheduled: Optional[int] = Field(None, ge=0)
    meetings_done: Optional[int] = Field(None, ge=0)
    days_since_first_contact: Optional[int] = Field(None, ge=0)
    follow_ups_total: Optional[int] = Field(None, ge=0)

    demo_requested: Optional[bool] = None
    budget_available: Optional[bool] = None
    decision_maker_contacted: Optional[bool] = None
    competitor_considering: Optional[bool] = None

    status: Optional[str] = Field(
        None, pattern=f"^({'|'.join(STATUSES)})$"
    )
    notes: Optional[str] = None
    revenue: Optional[float] = None


class LeadResponse(BaseModel):
    """Schema for lead data returned by the API."""

    id: UUID
    employee_id: UUID
    company_name: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    lead_source: str
    industry: str
    company_size: int
    website_visits: int
    emails_opened: int
    emails_clicked: int
    calls_made: int
    calls_connected: int
    call_duration_minutes: int
    meetings_scheduled: int
    meetings_done: int
    days_since_first_contact: int
    follow_ups_total: int
    demo_requested: bool
    budget_available: bool
    decision_maker_contacted: bool
    competitor_considering: bool
    status: str
    notes: Optional[str] = None
    revenue: float
    predicted_outcome: Optional[str] = None
    prediction_confidence: Optional[float] = None
    predicted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    """Paginated list of leads."""

    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
