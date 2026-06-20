from fastapi import APIRouter
from app.shared.presentation.schemas import PlaceholderResponse
from app.modules.companies.presentation.schemas import (
    CreateCompanyRequest, UpdateCompanyRequest, CompanyResponse,
    CompanySettingsResponse, UpdateCompanySettingsRequest,
    InviteCompanyUserRequest, UpdateCompanyUserRoleRequest
)

router = APIRouter()
users_router = APIRouter()

@router.get("", response_model=PlaceholderResponse)
def list_companies() -> PlaceholderResponse:
    # TODO: Call use case in application/use_cases
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="list_companies")

@router.post("", response_model=CompanyResponse)
def create_company(request: CreateCompanyRequest) -> CompanyResponse:
    return CompanyResponse(message="Endpoint scaffold ready", module="companies", action="create_company")

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: str) -> CompanyResponse:
    return CompanyResponse(message="Endpoint scaffold ready", module="companies", action="get_company", company_id=company_id)

@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: str, request: UpdateCompanyRequest) -> CompanyResponse:
    return CompanyResponse(message="Endpoint scaffold ready", module="companies", action="update_company", company_id=company_id)

@router.delete("/{company_id}", response_model=PlaceholderResponse)
def delete_company(company_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="delete_company")

@router.get("/{company_id}/settings", response_model=CompanySettingsResponse)
def get_company_settings(company_id: str) -> CompanySettingsResponse:
    return CompanySettingsResponse(message="Endpoint scaffold ready", module="companies", action="get_company_settings", company_id=company_id)

@router.patch("/{company_id}/settings", response_model=CompanySettingsResponse)
def update_company_settings(company_id: str, request: UpdateCompanySettingsRequest) -> CompanySettingsResponse:
    return CompanySettingsResponse(message="Endpoint scaffold ready", module="companies", action="update_company_settings", company_id=company_id)

@router.get("/{company_id}/activity", response_model=PlaceholderResponse)
def get_company_activity(company_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="get_company_activity")

@router.get("/{company_id}/summary", response_model=PlaceholderResponse)
def get_company_summary(company_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="get_company_summary")

@users_router.get("/{company_id}/users", response_model=PlaceholderResponse)
def list_company_users(company_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="list_company_users")

@users_router.post("/{company_id}/users/invite", response_model=PlaceholderResponse)
def invite_company_user(company_id: str, request: InviteCompanyUserRequest) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="invite_company_user")

@users_router.patch("/{company_id}/users/{user_id}/role", response_model=PlaceholderResponse)
def update_company_user_role(company_id: str, user_id: str, request: UpdateCompanyUserRoleRequest) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="update_company_user_role")

@users_router.delete("/{company_id}/users/{user_id}", response_model=PlaceholderResponse)
def delete_company_user(company_id: str, user_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="companies", action="delete_company_user")
