from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class CreateCompanyRequest(BaseModel):
    name: str

class UpdateCompanyRequest(BaseModel):
    name: str

class CompanyResponse(PlaceholderResponse):
    company_id: str | None = None

class CompanySettingsResponse(PlaceholderResponse):
    company_id: str | None = None

class UpdateCompanySettingsRequest(BaseModel):
    pass

class InviteCompanyUserRequest(BaseModel):
    email: str

class UpdateCompanyUserRoleRequest(BaseModel):
    role: str
