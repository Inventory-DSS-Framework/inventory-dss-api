from pydantic import BaseModel

class PlaceholderResponse(BaseModel):
    message: str
    module: str
    action: str
    status: str = "not_implemented"

class MessageResponse(BaseModel):
    message: str

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
