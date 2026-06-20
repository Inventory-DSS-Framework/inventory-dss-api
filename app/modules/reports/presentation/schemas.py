from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class CreateReportRequest(BaseModel):
    pass

class ReportResponse(PlaceholderResponse):
    pass

class ReportStatusResponse(PlaceholderResponse):
    pass

class ReportTemplateResponse(PlaceholderResponse):
    pass
