from api.schemas.user import (
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from api.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)
from api.schemas.dashboard import (
    AdminDashboard,
    AdminEmployeeDetail,
    AdminEmployeeListItem,
    AdminEmployeeListResponse,
    EmployeeDashboard,
    LeaderboardEntry,
    LeadsByStatusItem,
    LeadsByStatusResponse,
    MonthlyTrend,
    PerformanceItem,
    PerformanceResponse,
    RecentActivityItem,
    StatusDistribution,
)
from api.schemas.salary import (
    EmployeeSalaryInfo,
    PerformanceTargetCreate,
    PerformanceTargetResponse,
    PerformanceTargetUpdate,
    SalaryRuleCreate,
    SalaryRuleResponse,
    SalaryRuleUpdate,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "TokenResponse",
    "TokenRefresh",
    # Lead
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadListResponse",
    # Dashboard
    "EmployeeDashboard",
    "MonthlyTrend",
    "RecentActivityItem",
    "PerformanceItem",
    "PerformanceResponse",
    "LeadsByStatusItem",
    "LeadsByStatusResponse",
    "AdminDashboard",
    "AdminEmployeeListItem",
    "AdminEmployeeListResponse",
    "AdminEmployeeDetail",
    "LeaderboardEntry",
    "StatusDistribution",
    # Salary & Targets
    "SalaryRuleCreate",
    "SalaryRuleUpdate",
    "SalaryRuleResponse",
    "PerformanceTargetCreate",
    "PerformanceTargetUpdate",
    "PerformanceTargetResponse",
    "EmployeeSalaryInfo",
]
