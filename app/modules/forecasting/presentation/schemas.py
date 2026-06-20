from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class CreateForecastRunRequest(BaseModel):
    pass

class ForecastRunResponse(PlaceholderResponse):
    pass

class ExecuteForecastRequest(BaseModel):
    pass

class ExecuteForecastFromCsvRequest(BaseModel):
    pass

class ForecastResultResponse(PlaceholderResponse):
    pass

class ForecastMetricsResponse(PlaceholderResponse):
    pass

class ModelComparisonRequest(BaseModel):
    pass

class ModelComparisonResponse(PlaceholderResponse):
    pass
