from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class GenerateRecommendationsRequest(BaseModel):
    pass

class RecommendationResponse(PlaceholderResponse):
    pass

class RecommendationSummaryResponse(PlaceholderResponse):
    pass

class SimulateReorderRequest(BaseModel):
    pass

class SimulateCoverageRequest(BaseModel):
    pass
