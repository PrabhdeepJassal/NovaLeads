"""
LeadPredict — Authentication routes.

Handles user registration, login, token refresh, and profile management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.lead import Lead
from api.models.target import PerformanceTarget
from api.models.user import User
from api.middleware.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_token,
)
from api.schemas.user import (
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new user account.

    Creates a user with the ``employee`` role by default.
    Returns a JWT access token + refresh token on success.
    """
    # --- Check for duplicate email ---
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # --- Auto-generate emp_id ---
    max_emp_result = await db.execute(
        select(func.max(User.emp_id)).where(User.emp_id.isnot(None))
    )
    max_emp_id = max_emp_result.scalar()
    if max_emp_id:
        # Extract the numeric part, increment by 1
        num = int(max_emp_id.split("-")[1]) + 1
    else:
        num = 1
    emp_id = f"EMP-{num:03d}"

    # --- Create user ---
    user = User(
        emp_id=emp_id,
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        role=data.role,
        company_name=data.company_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # --- Auto-create current month PerformanceTarget for employees ---
    if user.role == "employee":
        from datetime import datetime, timezone

        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        target = PerformanceTarget(
            employee_id=user.id,
            month=current_month,
            revenue_target=100000.0,
            actual_revenue=0.0,
        )
        db.add(target)
        await db.flush()

    # --- Issue tokens ---
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return JWT tokens.

    On successful login, the user's ``prev_conversion_rate`` is recalculated
    from their existing leads.
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # --- Update prev_conversion_rate ---
    total_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.employee_id == user.id)
    )
    total = total_result.scalar() or 0

    converted_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.employee_id == user.id, Lead.status == "successful"
        )
    )
    converted = converted_result.scalar() or 0

    user.prev_conversion_rate = converted / total if total > 0 else 0.0
    await db.flush()

    # --- Issue tokens ---
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Issue a new access token using a valid refresh token."""
    payload = verify_token(data.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update the current user's profile (name, email, company_name)."""
    if data.name is not None:
        current_user.name = data.name
    if data.email is not None:
        # Check uniqueness
        existing = await db.execute(
            select(User).where(User.email == data.email, User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        current_user.email = data.email
    if data.company_name is not None:
        current_user.company_name = data.company_name

    await db.flush()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)
