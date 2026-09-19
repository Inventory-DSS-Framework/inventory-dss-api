"""Billing module domain — plan catalog (static; prices in PEN, IGV included)."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.modules.billing.domain.enums import BillingCycle

FREE_PLAN_ID = "free"
PREMIUM_PLAN_ID = "premium"
IGV_RATE = Decimal("0.18")


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    tagline: str
    price_monthly: Decimal
    price_yearly: Decimal
    features: tuple[str, ...] = field(default_factory=tuple)
    limits: tuple[str, ...] = field(default_factory=tuple)
    currency: str = "PEN"

    def price_for(self, cycle: BillingCycle) -> Decimal:
        return self.price_yearly if cycle == BillingCycle.YEARLY else self.price_monthly


PLANS: dict[str, Plan] = {
    FREE_PLAN_ID: Plan(
        id=FREE_PLAN_ID,
        name="Gratis",
        tagline="Tu ERP completo, sin costo.",
        price_monthly=Decimal("0.00"),
        price_yearly=Decimal("0.00"),
        features=(
            "Ventas y POS con boleta y factura",
            "Compras y proveedores",
            "Inventario y movimientos de stock",
            "Columnas personalizadas",
            "Usuarios vendedores",
            "Motor FTGM aplicado a 1 producto",
        ),
        limits=(
            "Pronóstico limitado a un solo producto",
            "Sin recomendaciones de compra automáticas",
            "Sin alertas ni reportes de pronóstico",
        ),
    ),
    PREMIUM_PLAN_ID: Plan(
        id=PREMIUM_PLAN_ID,
        name="Premium",
        tagline="Todo el Motor FTGM trabajando para tu negocio.",
        price_monthly=Decimal("149.00"),
        price_yearly=Decimal("1490.00"),
        features=(
            "Todo lo del plan Gratis",
            "Pronóstico de todo tu catálogo",
            "Pronóstico por proveedor, vendedor o categoría",
            "Pronosticado vs real (seguimiento)",
            "Recomendaciones de compra automáticas",
            "KPIs de cobertura y riesgo de quiebre",
            "Alertas de reposición",
            "Reportes y KPIs exportables",
        ),
    ),
}


def get_plan(plan_id: str) -> Plan | None:
    return PLANS.get(plan_id)
