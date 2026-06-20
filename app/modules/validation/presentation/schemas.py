from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class ValidationSessionRequest(BaseModel):
    pass

class ValidationSessionResponse(PlaceholderResponse):
    pass

class ValidationResponseRequest(BaseModel):
    pass

class ValidationResultsResponse(PlaceholderResponse):
    pass
