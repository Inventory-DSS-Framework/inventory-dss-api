"""Inventory module domain — enums."""
from __future__ import annotations

from enum import StrEnum


class MovementType(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    ADJUSTMENT = "adjustment"


class ReplenishmentStatus(StrEnum):
    SUGGESTED = "suggested"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"
