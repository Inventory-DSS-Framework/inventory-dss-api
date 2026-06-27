"""Companies module — presentation request schemas.

Responses reuse the application DTOs (CompanyDTO, UserDTO) as response models.
"""
from __future__ import annotations

from pydantic import BaseModel


class CreateCompanyRequest(BaseModel):
    name: str
    tax_id: str
    email: str
    business_type: str = ""
    address: str = ""
    phone: str = ""


class UpdateCompanyRequest(BaseModel):
    name: str | None = None
    business_type: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class InviteUserRequest(BaseModel):
    email: str
    full_name: str
    role: str = "viewer"
    temporary_password: str


class UpdateUserRoleRequest(BaseModel):
    role: str
