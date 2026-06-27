"""Companies module — use cases for the User aggregate."""
from __future__ import annotations

from uuid import UUID

from app.modules.companies.application.dtos import UserDTO
from app.modules.companies.domain.entities import User
from app.modules.companies.domain.enums import UserRole, UserStatus
from app.modules.companies.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.companies.domain.repositories import UserRepository
from app.shared.domain.value_objects import Email
from app.shared.infrastructure.security.hashing import hash_password


class InviteUser:
    """Creates a user in INVITED state with a (temporary) hashed password."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(
        self,
        company_id: UUID,
        *,
        email: str,
        full_name: str,
        role: UserRole,
        temporary_password: str,
    ) -> UserDTO:
        if self._users.get_by_email(email) is not None:
            raise UserAlreadyExistsError(email)
        user = User(
            company_id=company_id,
            email=Email(email),
            full_name=full_name,
            hashed_password=hash_password(temporary_password),
            role=role,
            status=UserStatus.INVITED,
        )
        return UserDTO.from_entity(self._users.add(user))


class GetUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> UserDTO:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        return UserDTO.from_entity(user)


class ListCompanyUsers:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(
        self, company_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[UserDTO]:
        return [
            UserDTO.from_entity(u)
            for u in self._users.list_by_company(company_id, offset, limit)
        ]


class UpdateUserRole:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID, *, role: UserRole) -> UserDTO:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        user.role = role
        return UserDTO.from_entity(self._users.update(user))


class DisableUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> UserDTO:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        user.disable()
        return UserDTO.from_entity(self._users.update(user))
