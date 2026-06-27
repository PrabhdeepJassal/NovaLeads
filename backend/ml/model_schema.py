"""
LeadPredict — Pydantic Schemas for the ML Layer.

These models are used both internally and by the API layer to validate
incoming prediction requests and format outgoing responses.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Input: Lead Features
# ---------------------------------------------------------------------------


class LeadFeatures(BaseModel):
    """All input features required by the LeadPredict model.

    Validation ensures types and ranges are sensible, catching bad data
    before it reaches the ML pipeline.
    """

    lead_source: str = Field(
        ...,
        description="Acquisition channel",
        examples=["Google Ads", "Facebook", "LinkedIn", "Referral", "Organic", "Cold Call", "Email Campaign"],
    )
    industry: str = Field(
        ...,
        description="Lead's industry vertical",
        examples=["Technology", "Healthcare", "Finance", "Education", "E-commerce", "Real Estate", "Manufacturing"],
    )
    company_size: int = Field(..., ge=1, le=5000, description="Number of employees")
    website_visits: int = Field(..., ge=0, le=50, description="Website visits in last 30 days")
    emails_opened: int = Field(..., ge=0, le=20, description="Emails opened")
    emails_clicked: int = Field(..., ge=0, le=10, description="Emails clicked")
    calls_made: int = Field(..., ge=0, le=15, description="Outbound calls made")
    calls_connected: int = Field(..., ge=0, le=10, description="Calls that connected")
    call_duration_minutes: int = Field(..., ge=0, le=300, description="Total minutes spent on calls")
    meetings_scheduled: int = Field(..., ge=0, le=5, description="Meetings scheduled")
    meetings_done: int = Field(..., ge=0, le=5, description="Meetings completed")
    days_since_first_contact: int = Field(..., ge=1, le=365, description="Days since lead entered pipeline")
    follow_ups_total: int = Field(..., ge=0, le=30, description="Total follow-up touches")
    demo_requested: bool = Field(..., description="Whether a product demo was requested")
    budget_available: bool = Field(..., description="Lead has confirmed budget")
    decision_maker_contacted: bool = Field(..., description="Spoke to a decision maker")
    competitor_considering: bool = Field(..., description="Lead is evaluating a competitor")
    employee_tenure_days: int = Field(..., ge=30, le=1000, description="Assigned employee's tenure at company")
    employee_prev_conversion_rate: float = Field(..., ge=0.0, le=1.0, description="Employee's historical conversion rate")

    # ---- Validators ----

    @field_validator("lead_source")
    @classmethod
    def validate_lead_source(cls, v: str) -> str:
        allowed = {
            "Google Ads", "Facebook", "LinkedIn", "Referral",
            "Organic", "Cold Call", "Email Campaign",
        }
        if v not in allowed:
            raise ValueError(
                f"lead_source must be one of {allowed}, got '{v}'"
            )
        return v

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, v: str) -> str:
        allowed = {
            "Technology", "Healthcare", "Finance", "Education",
            "E-commerce", "Real Estate", "Manufacturing",
        }
        if v not in allowed:
            raise ValueError(
                f"industry must be one of {allowed}, got '{v}'"
            )
        return v

    @field_validator("call_duration_minutes")
    @classmethod
    def call_duration_consistent(cls, v: int, info) -> int:
        calls_made = info.data.get("calls_made", 0)
        if calls_made == 0 and v > 0:
            raise ValueError("call_duration_minutes > 0 requires calls_made > 0")
        return v

    @field_validator("calls_connected")
    @classmethod
    def calls_connected_lte_calls_made(cls, v: int, info) -> int:
        calls_made = info.data.get("calls_made")
        if calls_made is not None and v > calls_made:
            raise ValueError("calls_connected cannot exceed calls_made")
        return v

    @field_validator("meetings_done")
    @classmethod
    def meetings_done_lte_scheduled(cls, v: int, info) -> int:
        scheduled = info.data.get("meetings_scheduled")
        if scheduled is not None and v > scheduled:
            raise ValueError("meetings_done cannot exceed meetings_scheduled")
        return v

    @field_validator("emails_clicked")
    @classmethod
    def emails_clicked_lte_opened(cls, v: int, info) -> int:
        opened = info.data.get("emails_opened")
        if opened is not None and v > opened:
            raise ValueError("emails_clicked cannot exceed emails_opened")
        return v

    @field_validator("employee_prev_conversion_rate")
    @classmethod
    def validate_conversion_rate(cls, v: float) -> float:
        return round(v, 4)

    class Config:
        json_schema_extra = {
            "example": {
                "lead_source": "Google Ads",
                "industry": "Technology",
                "company_size": 500,
                "website_visits": 30,
                "emails_opened": 12,
                "emails_clicked": 5,
                "calls_made": 8,
                "calls_connected": 4,
                "call_duration_minutes": 95,
                "meetings_scheduled": 3,
                "meetings_done": 2,
                "days_since_first_contact": 90,
                "follow_ups_total": 15,
                "demo_requested": True,
                "budget_available": True,
                "decision_maker_contacted": True,
                "competitor_considering": False,
                "employee_tenure_days": 500,
                "employee_prev_conversion_rate": 0.35,
            }
        }


# ---------------------------------------------------------------------------
# Output: Prediction Results
# ---------------------------------------------------------------------------


class PredictionResult(BaseModel):
    """Prediction output for a single lead."""

    probabilities: dict[Literal["cold", "rejected", "successful"], float] = Field(
        ...,
        description="Predicted probability for each class (sums to 1.0)",
        examples=[{"cold": 0.10, "rejected": 0.20, "successful": 0.70}],
    )
    predicted_class: Literal["cold", "rejected", "successful"] = Field(
        ...,
        description="Most likely class label",
        examples=["successful"],
    )
    predicted_class_code: Literal[0, 1, 2] = Field(
        ...,
        description="Numeric code: 0=cold, 1=rejected, 2=successful",
        examples=[2],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (max probability)",
        examples=[0.85],
    )
    top_factors: list[tuple[str, float]] = Field(
        ...,
        description="Top-5 features driving this prediction, each with a contribution score",
        examples=[[("meetings_done", 0.15), ("demo_requested", 0.12)]],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "probabilities": {"cold": 0.10, "rejected": 0.20, "successful": 0.70},
                "predicted_class": "successful",
                "predicted_class_code": 2,
                "confidence": 0.70,
                "top_factors": [
                    ("meetings_done", 0.15),
                    ("demo_requested", 0.12),
                    ("decision_maker_contacted", 0.10),
                    ("budget_available", 0.09),
                    ("employee_prev_conversion_rate", 0.08),
                ],
            }
        }


# ---------------------------------------------------------------------------
# Batch Request / Response
# ---------------------------------------------------------------------------


class BatchPredictionRequest(BaseModel):
    """Request body for batch predictions."""

    leads: list[LeadFeatures] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of leads to predict (1-1000)",
    )


class BatchPredictionResponse(BaseModel):
    """Response body for batch predictions."""

    results: list[PredictionResult] = Field(
        ...,
        description="One prediction result per input lead",
    )
    total: int = Field(..., description="Number of leads processed")
