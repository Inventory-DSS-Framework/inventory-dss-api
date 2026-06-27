"""Recommendations module domain — pure replenishment logic.

Given current stock, forecasted daily demand and inventory parameters, decides whether
to reorder and how much, using a classic order-up-to policy:

    reorder is triggered when stock <= reorder_point OR stock < demand(lead time)+safety
    target level (order-up-to) = demand(lead time + review period) + safety_stock
    suggested quantity = ceil(target - current stock)

Priority reflects urgency (how exposed the stock is over the lead time).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from app.modules.recommendations.domain.enums import RecommendationPriority


@dataclass(frozen=True)
class ReorderInputs:
    current_stock: int
    daily_demand: list[Decimal]  # predicted demand per day, horizon order
    lead_time_days: int
    safety_stock: int = 0
    reorder_point: int = 0
    review_days: int = 7


@dataclass(frozen=True)
class ReorderSuggestion:
    quantity: int
    priority: RecommendationPriority
    reason: str


def _window_sum(values: list[Decimal], days: int) -> Decimal:
    return sum(values[:days], Decimal("0")) if days > 0 else Decimal("0")


def suggest_reorder(inp: ReorderInputs) -> ReorderSuggestion | None:
    demand_lead = _window_sum(inp.daily_demand, inp.lead_time_days)
    demand_window = _window_sum(inp.daily_demand, inp.lead_time_days + inp.review_days)
    order_up_to = demand_window + Decimal(inp.safety_stock)

    exposure = demand_lead + Decimal(inp.safety_stock)
    triggered = inp.current_stock <= inp.reorder_point or (
        Decimal(inp.current_stock) < exposure
    )
    if not triggered:
        return None

    raw_qty = order_up_to - Decimal(inp.current_stock)
    if raw_qty <= 0:
        return None
    quantity = int(raw_qty.to_integral_value(rounding=ROUND_CEILING))

    if inp.current_stock <= inp.safety_stock:
        priority = RecommendationPriority.HIGH
    elif Decimal(inp.current_stock) < demand_lead:
        priority = RecommendationPriority.MEDIUM
    else:
        priority = RecommendationPriority.LOW

    reason = (
        f"Stock actual {inp.current_stock}; demanda estimada en lead time "
        f"({inp.lead_time_days}d) {demand_lead}. Reponer {quantity} unidades para "
        f"alcanzar el nivel objetivo {order_up_to}."
    )
    return ReorderSuggestion(quantity=quantity, priority=priority, reason=reason)
