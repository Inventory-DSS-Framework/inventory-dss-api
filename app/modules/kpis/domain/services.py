"""KPIs module domain — pure KPI formulas.

These are the analytical core of the DSS. Each function consumes a product's current
stock, its forecasted daily demand, and its inventory parameters, and returns a KPI
value. No I/O, no frameworks: the formulas are deterministic and unit-testable.

KPIs:
- coverage_days: how many days the current stock lasts at the forecasted demand rate.
- stockout_risk (0-100): shortfall risk over the lead time (demand + safety vs stock).
- turnover: forecasted demand over the horizon divided by current stock.
- overstock_risk (0-100): how much stock exceeds what is needed over the lead time.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.modules.kpis.domain.enums import KpiType

_COVERAGE_CAP = Decimal("9999")  # sentinel for "effectively infinite" coverage


def _clamp_pct(value: Decimal) -> Decimal:
    """Clamp a ratio (0..1) into a 0..100 percentage, rounded to 2 decimals."""
    pct = value * Decimal("100")
    pct = max(Decimal("0"), min(Decimal("100"), pct))
    return pct.quantize(Decimal("0.01"))


@dataclass(frozen=True)
class ProductKpiInputs:
    current_stock: int
    daily_demand: list[Decimal]  # predicted demand per day, in horizon order
    lead_time_days: int
    safety_stock: int = 0

    @property
    def total_demand(self) -> Decimal:
        return sum(self.daily_demand, Decimal("0"))

    @property
    def demand_over_lead_time(self) -> Decimal:
        window = self.daily_demand[: self.lead_time_days] if self.lead_time_days else []
        return sum(window, Decimal("0"))


def coverage_days(inp: ProductKpiInputs) -> Decimal:
    total = inp.total_demand
    horizon = len(inp.daily_demand)
    if total <= 0 or horizon == 0:
        return _COVERAGE_CAP if inp.current_stock > 0 else Decimal("0")
    avg_daily = total / Decimal(horizon)
    days = Decimal(inp.current_stock) / avg_daily
    return min(_COVERAGE_CAP, days.quantize(Decimal("0.01")))


def stockout_risk(inp: ProductKpiInputs) -> Decimal:
    needed = inp.demand_over_lead_time + Decimal(inp.safety_stock)
    if needed <= 0:
        return Decimal("0")
    shortfall = needed - Decimal(inp.current_stock)
    return _clamp_pct(shortfall / needed)


def turnover(inp: ProductKpiInputs) -> Decimal:
    if inp.current_stock <= 0:
        return Decimal("0")
    return (inp.total_demand / Decimal(inp.current_stock)).quantize(Decimal("0.0001"))


def overstock_risk(inp: ProductKpiInputs) -> Decimal:
    target = inp.demand_over_lead_time + Decimal(inp.safety_stock)
    if inp.current_stock <= 0:
        return Decimal("0")
    excess = Decimal(inp.current_stock) - target
    if excess <= 0:
        return Decimal("0")
    return _clamp_pct(excess / Decimal(inp.current_stock))


def compute_all(inp: ProductKpiInputs) -> dict[KpiType, Decimal]:
    return {
        KpiType.COVERAGE_DAYS: coverage_days(inp),
        KpiType.STOCKOUT_RISK: stockout_risk(inp),
        KpiType.TURNOVER: turnover(inp),
        KpiType.OVERSTOCK_RISK: overstock_risk(inp),
    }
