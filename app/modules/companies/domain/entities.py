"""Companies module domain — entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.modules.companies.domain.enums import (
    CompanyPlan,
    CompanyStatus,
    UserRole,
    UserStatus,
)
from app.modules.companies.domain.exceptions import (
    InvalidCompanyStateError,
    InvalidUserStateError,
)
from app.shared.domain.errors import ValidationError
from app.shared.domain.value_objects import Email


# Role-permission mapping (domain knowledge)
_ROLE_PERMISSIONS: dict[UserRole, frozenset[str]] = {
    UserRole.OWNER: frozenset({"read", "write", "delete", "analyze", "manage"}),
    UserRole.ADMIN: frozenset({"read", "write", "delete", "analyze", "manage"}),
    UserRole.ANALYST: frozenset({"read", "analyze"}),
    UserRole.VIEWER: frozenset({"read"}),
}


@dataclass
class Company:
    """Represents a company (tenant) in the system."""

    name: str
    tax_id: str
    business_type: str
    address: str
    phone: str
    email: Email
    plan: CompanyPlan = CompanyPlan.FREE
    status: CompanyStatus = CompanyStatus.ACTIVE
    id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError(message="Company name cannot be empty")
        if not self.tax_id.strip():
            raise ValidationError(message="Company tax_id (RUC) cannot be empty")

    def suspend(self) -> None:
        """Suspend this company."""
        if self.status == CompanyStatus.SUSPENDED:
            raise InvalidCompanyStateError(
                message="Company is already suspended"
            )
        self.status = CompanyStatus.SUSPENDED

    def activate(self) -> None:
        """Activate this company."""
        if self.status == CompanyStatus.ACTIVE:
            raise InvalidCompanyStateError(
                message="Company is already active"
            )
        self.status = CompanyStatus.ACTIVE


@dataclass
class User:
    """Represents a user belonging to a company."""

    company_id: UUID
    email: Email
    full_name: str
    hashed_password: str
    role: UserRole = UserRole.VIEWER
    status: UserStatus = UserStatus.INVITED
    last_login_at: datetime | None = None
    id: UUID | None = None

    def can(self, permission: str) -> bool:
        """Check whether the user's role grants the given permission."""
        return permission in _ROLE_PERMISSIONS.get(self.role, frozenset())

    def disable(self) -> None:
        """Disable this user account."""
        if self.status == UserStatus.DISABLED:
            raise InvalidUserStateError(
                message="User is already disabled"
            )
        self.status = UserStatus.DISABLED

    def record_login(self) -> None:
        """Record the current time as the last login."""
        self.last_login_at = datetime.now(timezone.utc)
