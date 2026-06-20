from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class CreatePreparationRunRequest(BaseModel):
    pass

class PreparationRunResponse(PlaceholderResponse):
    pass

class PreparationStatusResponse(PlaceholderResponse):
    pass

class CleanDataRequest(BaseModel):
    pass

class NormalizeDataRequest(BaseModel):
    pass

class DetectOutliersRequest(BaseModel):
    pass

class DetectStockoutsRequest(BaseModel):
    pass

class BuildTimeSeriesRequest(BaseModel):
    pass

class DataQualityReportResponse(PlaceholderResponse):
    pass
