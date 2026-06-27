"""Billing module — HTTP router."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.modules.billing.application.use_cases.billing import (
    GetSubscription,
    UpdateSubscriptionStatus,
)
from app.modules.billing.domain.repositories import SubscriptionRepository
from app.modules.billing.presentation.dependencies import get_subscription_repository
from app.modules.billing.presentation.schemas import (
    InvoiceResponse,
    PaymentWebhookResponse,
    PlanResponse,
    SubscriptionRequest,
    SubscriptionResponse,
    WebhookUpdateSubscriptionRequest,
)
from app.shared.presentation.deps import AuthenticatedUser, require_company_access
from app.shared.presentation.schemas import PlaceholderResponse

router = APIRouter()
companies_router = APIRouter()


# --- Global Billing Endpoints ---

@router.get("/plans", response_model=PlaceholderResponse)
def list_plans() -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="list_plans")


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str) -> PlanResponse:
    return PlanResponse(message="Endpoint scaffold ready", module="billing", action="get_plan")


@router.post("/webhooks/payment-provider", response_model=PaymentWebhookResponse)
def payment_webhook() -> PaymentWebhookResponse:
    return PaymentWebhookResponse(message="Endpoint scaffold ready", module="billing", action="payment_webhook")


# Let's add a fake webhook endpoint here for testing updates to a company's subscription easily
@router.post("/webhooks/simulate/{company_id}", response_model=SubscriptionResponse)
def simulate_webhook_update(
    company_id: UUID,
    request: WebhookUpdateSubscriptionRequest,
    repo: Annotated[SubscriptionRepository, Depends(get_subscription_repository)],
) -> SubscriptionResponse:
    """Simulates a webhook from a payment provider to update the subscription."""
    use_case = UpdateSubscriptionStatus(repo)
    dto = use_case.execute(
        company_id=company_id,
        status=request.status,
        plan_id=request.plan_id,
        period_start=request.current_period_start,
        period_end=request.current_period_end,
    )
    return SubscriptionResponse.model_validate(dto)


# --- Company Billing Endpoints ---

@companies_router.get("/{company_id}/billing/subscription", response_model=SubscriptionResponse)
def get_company_subscription(
    company_id: UUID,
    repo: Annotated[SubscriptionRepository, Depends(get_subscription_repository)],
    user: Annotated[AuthenticatedUser, Depends(require_company_access)],
) -> SubscriptionResponse:
    use_case = GetSubscription(repo)
    dto = use_case.execute(company_id=company_id)
    return SubscriptionResponse.model_validate(dto)


@companies_router.post("/{company_id}/billing/subscription", response_model=PlaceholderResponse)
def create_company_subscription(company_id: UUID, request: SubscriptionRequest) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="create_company_subscription")


@companies_router.patch("/{company_id}/billing/subscription", response_model=PlaceholderResponse)
def update_company_subscription(company_id: UUID) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="update_company_subscription")


@companies_router.delete("/{company_id}/billing/subscription", response_model=PlaceholderResponse)
def delete_company_subscription(company_id: UUID) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="delete_company_subscription")


@companies_router.get("/{company_id}/billing/invoices", response_model=PlaceholderResponse)
def list_company_invoices(company_id: UUID) -> PlaceholderResponse:
    return PlaceholderResponse(message="Endpoint scaffold ready", module="billing", action="list_company_invoices")


@companies_router.get("/{company_id}/billing/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_company_invoice(company_id: UUID, invoice_id: UUID) -> InvoiceResponse:
    return InvoiceResponse(message="Endpoint scaffold ready", module="billing", action="get_company_invoice")
