from fastapi import APIRouter
from app.shared.presentation.schemas import PlaceholderResponse
from app.modules.auth.presentation.schemas import RegisterRequest, LoginRequest, TokenResponse, CurrentUserResponse

router = APIRouter()

@router.post("/register", response_model=PlaceholderResponse)
def register(request: RegisterRequest) -> PlaceholderResponse:
    # TODO: Call use case in application/use_cases
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="register")

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    return TokenResponse(message="Endpoint scaffold ready", module="auth", action="login")

@router.post("/logout", response_model=PlaceholderResponse)
def logout() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="logout")

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token() -> TokenResponse:
    return TokenResponse(message="Endpoint scaffold ready", module="auth", action="refresh_token")

@router.get("/me", response_model=CurrentUserResponse)
def get_me() -> CurrentUserResponse:
    return CurrentUserResponse(message="Endpoint scaffold ready", module="auth", action="get_me")

@router.patch("/me", response_model=CurrentUserResponse)
def update_me() -> CurrentUserResponse:
    return CurrentUserResponse(message="Endpoint scaffold ready", module="auth", action="update_me")

@router.patch("/me/password", response_model=PlaceholderResponse)
def update_password() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="update_password")

@router.post("/forgot-password", response_model=PlaceholderResponse)
def forgot_password() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="forgot_password")

@router.post("/reset-password", response_model=PlaceholderResponse)
def reset_password() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="reset_password")

@router.post("/verify-email", response_model=PlaceholderResponse)
def verify_email() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="verify_email")

@router.post("/resend-verification", response_model=PlaceholderResponse)
def resend_verification() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="auth", action="resend_verification")
