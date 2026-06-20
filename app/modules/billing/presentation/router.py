from fastapi import APIRouter
from app.shared.presentation.schemas import PlaceholderResponse
from app.modules.billing.presentation.schemas import (
    PlanResponse, SubscriptionRequest, SubscriptionResponse,
    InvoiceResponse, PaymentWebhookResponse
)

router = APIRouter()
companies_router = APIRouter()

@router.get("/plans", response_model=PlaceholderResponse)
def list_plans() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="list_plans")

@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str) -> PlanResponse:
    return PlanResponse(message="Endpoint scaffold ready", module="billing", action="get_plan")

@router.post("/webhooks/payment-provider", response_model=PaymentWebhookResponse)
def payment_webhook() -> PaymentWebhookResponse:
    return PaymentWebhookResponse(message="Endpoint scaffold ready", module="billing", action="payment_webhook")

@companies_router.get("/{company_id}/billing/subscription", response_model=SubscriptionResponse)
def get_company_subscription(company_id: str) -> SubscriptionResponse:
    return SubscriptionResponse(message="Endpoint scaffold ready", module="billing", action="get_company_subscription")

@companies_router.post("/{company_id}/billing/subscription", response_model=SubscriptionResponse)
def create_company_subscription(company_id: str, request: SubscriptionRequest) -> SubscriptionResponse:
    return SubscriptionResponse(message="Endpoint scaffold ready", module="billing", action="create_company_subscription")

@companies_router.patch("/{company_id}/billing/subscription", response_model=SubscriptionResponse)
def update_company_subscription(company_id: str) -> SubscriptionResponse:
    return SubscriptionResponse(message="Endpoint scaffold ready", module="billing", action="update_company_subscription")

@companies_router.delete("/{company_id}/billing/subscription", response_model=PlaceholderResponse)
def delete_company_subscription(company_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="delete_company_subscription")

@companies_router.get("/{company_id}/billing/invoices", response_model=PlaceholderResponse)
def list_company_invoices(company_id: str) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="list_company_invoices")

@companies_router.get("/{company_id}/billing/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_company_invoice(company_id: str, invoice_id: str) -> InvoiceResponse:
    return InvoiceResponse(message="Endpoint scaffold ready", module="billing", action="get_company_invoice")
