from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class UploadDatasetResponse(PlaceholderResponse):
    pass

class DatasetUploadResponse(PlaceholderResponse):
    pass

class DatasetValidationResponse(PlaceholderResponse):
    pass

class DatasetErrorResponse(PlaceholderResponse):
    pass

class ColumnMappingRequest(BaseModel):
    pass

class ColumnMappingResponse(PlaceholderResponse):
    pass

class DatasetPreviewResponse(PlaceholderResponse):
    pass
