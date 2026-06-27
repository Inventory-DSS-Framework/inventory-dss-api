"""Billing module domain — enums."""
from __future__ import annotations

from enum import StrEnum


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
