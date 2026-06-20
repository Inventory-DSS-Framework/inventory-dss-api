from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class NotificationResponse(PlaceholderResponse):
    pass

class CreateNotificationRequest(BaseModel):
    pass

class NotificationPreferencesResponse(PlaceholderResponse):
    pass

class UpdateNotificationPreferencesRequest(BaseModel):
    pass
