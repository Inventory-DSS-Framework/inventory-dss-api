from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class AdminUserResponse(PlaceholderResponse):
    pass

class AdminCompanyResponse(PlaceholderResponse):
    pass

class AdminSystemStatusResponse(PlaceholderResponse):
    pass
