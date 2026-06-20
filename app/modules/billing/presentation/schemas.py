from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class PlanResponse(PlaceholderResponse):
    pass

class SubscriptionRequest(BaseModel):
    pass

class SubscriptionResponse(PlaceholderResponse):
    pass

class InvoiceResponse(PlaceholderResponse):
    pass

class PaymentWebhookResponse(PlaceholderResponse):
    pass
