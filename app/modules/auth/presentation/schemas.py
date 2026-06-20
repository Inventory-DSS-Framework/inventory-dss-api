from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(PlaceholderResponse):
    pass

class CurrentUserResponse(PlaceholderResponse):
    pass
