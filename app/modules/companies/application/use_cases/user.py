"""Companies module — use cases for the User aggregate."""
from __future__ import annotations

from uuid import UUID

from app.modules.companies.application.dtos import UserDTO
from app.modules.companies.domain.entities import User
from app.modules.companies.domain.enums import UserRole, UserStatus
from app.modules.companies.domain.exceptions import (
    InvalidUserStateError,
    UserAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.companies.domain.repositories import UserRepository
from app.shared.domain.value_objects import Email
from app.shared.infrastructure.security.hashing import hash_password

MIN_PASSWORD_LENGTH = 6


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


class CreateCompanyUser:
    """An owner/admin creates a user that signs in with a username (e.g. a seller)."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(
        self,
        company_id: UUID,
        *,
        full_name: str,
        username: str,
        password: str,
        role: UserRole,
    ) -> UserDTO:
        if role not in (UserRole.SELLER, UserRole.ADMIN):
            raise InvalidUserStateError(message="Solo se pueden crear usuarios vendedor o administrador")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidUserStateError(
                message=f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
            )
        normalized = username.strip().lower()
        if self._users.get_by_username(normalized) is not None:
            raise UsernameAlreadyExistsError(normalized)
        user = User(
            company_id=company_id,
            email=None,
            username=normalized,
            full_name=full_name.strip(),
            hashed_password=hash_password(password),
            role=role,
            status=UserStatus.ACTIVE,
        )
        return UserDTO.from_entity(self._users.add(user))


class UpdateCompanyUser:
    """Rename, reset the password, or enable/disable a user of the same company."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(
        self,
        company_id: UUID,
        user_id: UUID,
        *,
        acting_user_id: UUID,
        full_name: str | None = None,
        password: str | None = None,
        status: UserStatus | None = None,
    ) -> UserDTO:
        user = self._users.get_by_id(user_id)
        if user is None or user.company_id != company_id:
            raise UserNotFoundError(str(user_id))
        if full_name is not None:
            if not full_name.strip():
                raise InvalidUserStateError(message="El nombre completo es obligatorio")
            user.full_name = full_name.strip()
        if password is not None:
            if len(password) < MIN_PASSWORD_LENGTH:
                raise InvalidUserStateError(
                    message=f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
                )
            user.hashed_password = hash_password(password)
        if status is not None and status != user.status:
            if user.id == acting_user_id:
                raise InvalidUserStateError(message="No puedes cambiar el estado de tu propio usuario")
            if user.role == UserRole.OWNER:
                raise InvalidUserStateError(message="El propietario de la cuenta no se puede desactivar")
            if status == UserStatus.DISABLED:
                user.disable()
            elif status == UserStatus.ACTIVE:
                user.activate()
            else:
                raise InvalidUserStateError(message="Estado no válido")
        return UserDTO.from_entity(self._users.update(user))


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
