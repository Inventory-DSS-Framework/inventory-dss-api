from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class CreateSaleRequest(BaseModel):
    pass

class UpdateSaleRequest(BaseModel):
    pass

class BulkSalesRequest(BaseModel):
    pass

class SaleResponse(PlaceholderResponse):
    company_id: str | None = None
    sale_id: str | None = None

class SalesSummaryResponse(PlaceholderResponse):
    pass

class SalesTimeSeriesResponse(PlaceholderResponse):
    pass

class CreateSalesBatchRequest(BaseModel):
    pass

class SalesBatchResponse(PlaceholderResponse):
    pass
