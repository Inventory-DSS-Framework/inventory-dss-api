"""Companies module domain — exceptions."""
from __future__ import annotations

from uuid import UUID

from app.shared.domain.errors import ConflictError, NotFoundError, ValidationError


class CompanyNotFoundError(NotFoundError):
    def __init__(self, company_id: UUID) -> None:
        super().__init__(
            message=f"Company with id '{company_id}' not found",
            details={"company_id": str(company_id)},
        )


class CompanyAlreadyExistsError(ConflictError):
    def __init__(self, tax_id: str) -> None:
        super().__init__(
            message=f"Company with tax_id '{tax_id}' already exists",
            details={"tax_id": tax_id},
        )


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            message=f"User '{identifier}' not found",
            details={"identifier": identifier},
        )


class UserAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"User with email '{email}' already exists",
            details={"email": email},
        )


class InvalidCompanyStateError(ValidationError):
    pass


class InvalidUserStateError(ValidationError):
    pass
