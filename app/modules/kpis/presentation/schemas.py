from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class KpiDashboardResponse(PlaceholderResponse):
    pass

class KpiSummaryResponse(PlaceholderResponse):
    pass

class KpiSnapshotRequest(BaseModel):
    pass

class KpiSnapshotResponse(PlaceholderResponse):
    pass

class CalculateKpisRequest(BaseModel):
    pass

class ProductKpiResponse(PlaceholderResponse):
    pass
