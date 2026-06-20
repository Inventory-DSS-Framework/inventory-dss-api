from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class CreateProductRequest(BaseModel):
    name: str

class UpdateProductRequest(BaseModel):
    name: str

class BulkProductRequest(BaseModel):
    pass

class ProductResponse(PlaceholderResponse):
    company_id: str | None = None
    product_id: str | None = None

class ProductSummaryResponse(PlaceholderResponse):
    company_id: str | None = None
    product_id: str | None = None
