"""
LeadPredict — Pydantic schemas for User authentication & profile.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for registering a new user."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)
    company_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="employee", pattern="^(employee|admin)$")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for public user data returned by the API."""

    id: UUID
    emp_id: Optional[str] = None
    email: str
    name: str
    role: str
    company_name: str
    is_active: bool
    employee_tenure_days: int
    prev_conversion_rate: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating the current user's profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)


class TokenResponse(BaseModel):
    """Schema returned after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    """Schema for refreshing an access token."""

    refresh_token: str
