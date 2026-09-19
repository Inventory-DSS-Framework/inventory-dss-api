"""Sales module — bulk sales from a spreadsheet, in two modes.

* **History** (``affect_stock=False``): a business moving onto the ERP brings its past
  sales (an export of its old system or its Excel). The rows become sale lines without a
  POS ticket, grouped in a sales batch. They feed Ventas › Historial importado, the
  product 360 view and the FTGM engine, but do NOT move stock — the current stock already
  reflects them (it comes from the inventory import).
* **Bulk sales** (``affect_stock=True``): day-to-day sales registered in bulk (another
  channel, a market day, an online store export). Same sale lines, plus an outbound
  inventory movement per line at the weighted-average cost; a row that would leave the
  product below zero is rejected and reported.

Each row is matched to a product by code (SKU), then barcode, then exact name. Invalid
rows are reported and skipped; the rest is imported. Re-uploading the same file is
detected and refused, so sales never double.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.inventory.infrastructure.persistence.models import InventoryMovementModel
from app.modules.inventory.infrastructure.persistence.queries import stock_on_hand_map
from app.modules.products.infrastructure.persistence.models import ProductModel
from app.modules.sales.infrastructure.persistence.models import SaleModel, SalesBatchModel
from app.shared.domain.errors import ConflictError, ValidationError

LIMA = timezone(timedelta(hours=-5))
TWO = Decimal("0.01")


def _norm(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def import_sales_history(
    session: Session,
    company_id: UUID,
    rows: list[dict[str, Any]],
    *,
    allow_duplicates: bool = False,
    affect_stock: bool = False,
) -> dict[str, Any]:
    if not rows:
        raise ValidationError(message="El archivo no tiene filas de ventas.")

    products = session.execute(
        select(ProductModel).where(ProductModel.company_id == company_id)
    ).scalars().all()
    by_sku = {_norm(p.sku): p for p in products}
    by_barcode = {_norm(p.barcode): p for p in products if p.barcode}
    by_name = {_norm(p.name): p for p in products}

    today = datetime.now(LIMA).date()
    errors: list[dict[str, Any]] = []
    valid: list[tuple[int, ProductModel, date, int, Decimal, str]] = []

    for i, row in enumerate(rows, start=1):
        n = int(row.get("row") or i)
        code, barcode, name = _norm(row.get("code")), _norm(row.get("barcode")), _norm(row.get("name"))
        product = (
            (by_sku.get(code) if code else None)
            or (by_barcode.get(code) if code else None)
            or (by_barcode.get(barcode) if barcode else None)
            or (by_name.get(name) if name else None)
        )
        if product is None:
            label = row.get("code") or row.get("barcode") or row.get("name") or "sin identificar"
            errors.append({"row": n, "message": f"Producto «{label}» no existe en tu inventario. Impórtalo primero."})
            continue

        try:
            sale_date = date.fromisoformat(str(row.get("sale_date") or "")[:10])
        except ValueError:
            errors.append({"row": n, "message": "Fecha inválida o vacía."})
            continue
        if sale_date > today:
            errors.append({"row": n, "message": f"La fecha {sale_date:%d/%m/%Y} está en el futuro."})
            continue

        try:
            qty_dec = Decimal(str(row.get("quantity")))
        except Exception:  # noqa: BLE001
            errors.append({"row": n, "message": "Cantidad inválida."})
            continue
        if qty_dec <= 0 or qty_dec != qty_dec.to_integral_value():
            errors.append({"row": n, "message": "La cantidad debe ser un entero mayor que 0."})
            continue

        raw_price = row.get("unit_price")
        try:
            price = (Decimal(str(raw_price)) if raw_price not in (None, "") else Decimal(product.unit_price)).quantize(
                TWO, rounding=ROUND_HALF_UP
            )
        except Exception:  # noqa: BLE001
            errors.append({"row": n, "message": "Precio unitario inválido."})
            continue
        if price < 0:
            errors.append({"row": n, "message": "El precio no puede ser negativo."})
            continue

        valid.append((n, product, sale_date, int(qty_dec), price, str(row.get("seller_name") or "").strip()[:255]))

    # Bulk sales take real stock out: walk the rows in date order and refuse any line
    # that asks for more units than are left at that point.
    if affect_stock and valid:
        on_hand = stock_on_hand_map(session, company_id)
        accepted = []
        for item in sorted(valid, key=lambda v: (v[2], v[0])):
            n, product, _, qty, _, _ = item
            available = on_hand.get(product.id, 0)
            if qty > available:
                errors.append({
                    "row": n,
                    "message": f"Stock insuficiente de «{product.name}»: pediste {qty}, quedan {max(available, 0)}.",
                })
                continue
            on_hand[product.id] = available - qty
            accepted.append(item)
        valid = accepted

    errors.sort(key=lambda e: e["row"])
    if not valid:
        return {
            "batch_id": None, "created": 0, "units": 0, "revenue": Decimal("0"),
            "period_start": None, "period_end": None, "products": 0, "errors": errors,
        }

    start = min(v[2] for v in valid)
    end = max(v[2] for v in valid)

    # Same file uploaded twice? Compare against the ticket-less sales already stored.
    if not allow_duplicates:
        existing = Counter(
            (pid, d, q, Decimal(pr).quantize(TWO))
            for pid, d, q, pr in session.execute(
                select(SaleModel.product_id, SaleModel.sale_date, SaleModel.quantity, SaleModel.unit_price).where(
                    SaleModel.company_id == company_id,
                    SaleModel.order_id.is_(None),
                    SaleModel.sale_date >= start,
                    SaleModel.sale_date <= end,
                )
            ).all()
        )
        incoming = Counter((p.id, d, q, pr) for _, p, d, q, pr, _ in valid)
        repeated = sum(min(c, existing[k]) for k, c in incoming.items())
        if repeated >= max(1, int(len(valid) * 0.9)):
            raise ConflictError(
                message="Estas ventas ya fueron cargadas antes (mismas fechas, productos, cantidades y precios). "
                "No se volvieron a cargar para no duplicarlas."
            )

    label = "Carga masiva de ventas" if affect_stock else "Importación de ventas"
    batch = SalesBatchModel(
        company_id=company_id,
        source_file=f"{label} {datetime.now(LIMA):%d/%m/%Y %H:%M}",
        status="completed",
        row_count=len(valid),
        period_start=start,
        period_end=end,
    )
    session.add(batch)
    session.flush()

    units = 0
    revenue = Decimal("0")
    for _, product, sale_date, qty, price, seller in valid:
        total = (price * qty).quantize(TWO, rounding=ROUND_HALF_UP)
        session.add(
            SaleModel(
                company_id=company_id,
                product_id=product.id,
                batch_id=batch.id,
                sale_date=sale_date,
                quantity=qty,
                unit_price=price,
                total_amount=total,
                currency=product.currency or "PEN",
                seller_name=seller,
                unit_cost=product.unit_cost,
            )
        )
        if affect_stock:
            session.add(
                InventoryMovementModel(
                    company_id=company_id,
                    product_id=product.id,
                    movement_type="outbound",
                    quantity=qty,
                    reason="Venta (carga masiva)",
                    occurred_at=datetime.combine(sale_date, time(12, 0), LIMA),
                    unit_cost=product.unit_cost,
                    reference_type="sale",
                    reference_id=batch.id,
                )
            )
        units += qty
        revenue += total
    session.flush()

    return {
        "batch_id": batch.id,
        "created": len(valid),
        "units": units,
        "revenue": revenue,
        "period_start": start,
        "period_end": end,
        "products": len({v[1].id for v in valid}),
        "errors": errors,
    }
