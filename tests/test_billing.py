"""Tests for Billing module."""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.modules.billing.application.use_cases.billing import (
    GetSubscription,
    UpdateSubscriptionStatus,
)
from app.modules.billing.domain.entities import Subscription
from app.modules.billing.domain.enums import SubscriptionStatus
from app.modules.billing.domain.exceptions import SubscriptionNotFoundError


class FakeSubscriptionRepository:
    def __init__(self) -> None:
        self._store: dict[UUID, Subscription] = {}

    def get_by_company(self, company_id: UUID) -> Subscription | None:
        return self._store.get(company_id)

    def add(self, subscription: Subscription) -> Subscription:
        if subscription.id is None:
            subscription.id = uuid4()
        self._store[subscription.company_id] = subscription
        return subscription

    def update(self, subscription: Subscription) -> Subscription:
        assert subscription.id is not None
        self._store[subscription.company_id] = subscription
        return subscription


class TestBillingUseCases:
    def test_update_and_get_subscription(self) -> None:
        repo = FakeSubscriptionRepository()
        company_id = uuid4()

        # Update (creates since it doesn't exist)
        updated = UpdateSubscriptionStatus(repo).execute(
            company_id=company_id,
            status=SubscriptionStatus.ACTIVE,
            plan_id="pro_plan",
        )
        assert updated.plan_id == "pro_plan"
        assert updated.status == SubscriptionStatus.ACTIVE

        # Get
        got = GetSubscription(repo).execute(company_id=company_id)
        assert got.id == updated.id

        # Update again (updates existing)
        updated2 = UpdateSubscriptionStatus(repo).execute(
            company_id=company_id,
            status=SubscriptionStatus.CANCELED,
        )
        assert updated2.status == SubscriptionStatus.CANCELED

    def test_get_unknown_subscription_raises(self) -> None:
        repo = FakeSubscriptionRepository()
        with pytest.raises(SubscriptionNotFoundError):
            GetSubscription(repo).execute(company_id=uuid4())
