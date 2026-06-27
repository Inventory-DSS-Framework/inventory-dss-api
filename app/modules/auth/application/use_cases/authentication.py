"""Auth module — authentication use cases.

Auth does not own the User entity (it lives in `companies`); it consumes the
CompanyRepository and UserRepository ports plus the shared security primitives.
"""
from __future__ import annotations

from uuid import UUID

from app.modules.auth.application.dtos import TokenDTO
from app.modules.companies.application.dtos import UserDTO
from app.modules.companies.domain.entities import Company, User
from app.modules.companies.domain.enums import (
    CompanyStatus,
    UserRole,
    UserStatus,
)
from app.modules.companies.domain.exceptions import (
    CompanyAlreadyExistsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.companies.domain.repositories import (
    CompanyRepository,
    UserRepository,
)
from app.shared.domain.errors import ForbiddenError, UnauthorizedError
from app.shared.domain.value_objects import Email
from app.shared.infrastructure.security.hashing import hash_password, verify_password
from app.shared.infrastructure.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def _issue_tokens(user: User) -> TokenDTO:
    """Build access + refresh tokens carrying tenant and role claims."""
    claims = {"company_id": str(user.company_id), "role": user.role.value}
    return TokenDTO(
        access_token=create_access_token(subject=str(user.id), extra_claims=claims),
        refresh_token=create_refresh_token(subject=str(user.id)),
    )


class RegisterAccount:
    """Sign up flow: create a Company and its OWNER user atomically."""

    def __init__(self, companies: CompanyRepository, users: UserRepository) -> None:
        self._companies = companies
        self._users = users

    def execute(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        company_name: str,
        tax_id: str,
        business_type: str = "",
    ) -> TokenDTO:
        if self._companies.get_by_tax_id(tax_id) is not None:
            raise CompanyAlreadyExistsError(tax_id)
        if self._users.get_by_email(email) is not None:
            raise UserAlreadyExistsError(email)

        company = self._companies.add(
            Company(
                name=company_name,
                tax_id=tax_id,
                business_type=business_type,
                address="",
                phone="",
                email=Email(email),
                status=CompanyStatus.ACTIVE,
            )
        )
        owner = self._users.add(
            User(
                company_id=company.id,  # type: ignore[arg-type]
                email=Email(email),
                full_name=full_name,
                hashed_password=hash_password(password),
                role=UserRole.OWNER,
                status=UserStatus.ACTIVE,
            )
        )
        return _issue_tokens(owner)


class Login:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, *, email: str, password: str) -> TokenDTO:
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError(message="Invalid email or password")
        if user.status == UserStatus.DISABLED:
            raise ForbiddenError(message="User account is disabled")
        user.record_login()
        self._users.update(user)
        return _issue_tokens(user)


class RefreshToken:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, *, refresh_token: str) -> TokenDTO:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError(message="Not a refresh token")
        subject = payload.get("sub")
        if not subject:
            raise UnauthorizedError(message="Invalid token subject")
        user = self._users.get_by_id(UUID(subject))
        if user is None:
            raise UnauthorizedError(message="User no longer exists")
        if user.status == UserStatus.DISABLED:
            raise ForbiddenError(message="User account is disabled")
        return _issue_tokens(user)


class GetCurrentUserProfile:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> UserDTO:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        return UserDTO.from_entity(user)


class ChangePassword:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(
        self, user_id: UUID, *, current_password: str, new_password: str
    ) -> None:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError(message="Current password is incorrect")
        user.hashed_password = hash_password(new_password)
        self._users.update(user)
