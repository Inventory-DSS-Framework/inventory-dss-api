"""Billing module — dependencies."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.billing.domain.repositories import SubscriptionRepository
from app.modules.billing.infrastructure.persistence.repositories import (
    SqlSubscriptionRepository,
)
from app.shared.presentation.deps import get_db


def get_subscription_repository(
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionRepository:
    """Dependency provider for SubscriptionRepository."""
    return SqlSubscriptionRepository(db)
