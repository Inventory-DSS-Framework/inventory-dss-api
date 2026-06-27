from typing import Callable
from uuid import UUID
from fastapi import Depends, Query
from pydantic import BaseModel
from app.shared.infrastructure.database.database import get_db
from app.shared.infrastructure.security.jwt import decode_token
from app.shared.infrastructure.security.auth import oauth2_scheme
from app.shared.presentation.schemas import PaginationParams
from app.shared.domain.errors import UnauthorizedError, ForbiddenError

# Re-export
__all__ = ["get_db", "get_pagination", "get_current_user", "require_company_access", "require_role"]

def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size")
) -> PaginationParams:
    """Dependency to get pagination parameters."""
    return PaginationParams(page=page, size=size)

class AuthenticatedUser(BaseModel):
    """Minimal representation of a user from JWT claims."""
    user_id: UUID
    company_id: UUID
    role: str

def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """Dependency to get the current authenticated user from the JWT token."""
    payload = decode_token(token)
    user_id_str = payload.get("sub")
    company_id_str = payload.get("company_id")
    role = payload.get("role")
    
    if not user_id_str or not company_id_str or not role:
        raise UnauthorizedError(message="Invalid token claims: missing required fields.")
        
    try:
        user_id = UUID(user_id_str)
        company_id = UUID(company_id_str)
    except ValueError:
        raise UnauthorizedError(message="Invalid token claims: malformed UUIDs.")

    return AuthenticatedUser(
        user_id=user_id,
        company_id=company_id,
        role=role
    )

def require_company_access(company_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """Validates that the current user has access to the requested company_id."""
    if current_user.company_id != company_id:
        raise ForbiddenError(message="You do not have access to this company's resources.")
    return current_user

def require_role(*allowed_roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Factory dependency to restrict access based on user role."""
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(message=f"Access denied. Required roles: {', '.join(allowed_roles)}")
        return current_user
    return role_checker
