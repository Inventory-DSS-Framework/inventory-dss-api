"""Sales module — import historical sales from a spreadsheet.

A business moving onto the ERP brings its past sales (an export of its old system or
its Excel). Those rows become *history*: sale lines without a POS ticket, grouped in a
sales batch. They feed Ventas › Historial importado, the product 360 view and the FTGM
engine, but they do NOT move stock — the current stock already reflects them (it comes
from the inventory import).

Each row is matched to a product by code (SKU), then barcode, then exact name. Rows
that don't match, or have a bad date/quantity, are reported and skipped; the rest is
imported. Re-uploading the same file is detected and refused, so history never doubles.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    valid: list[tuple[ProductModel, date, int, Decimal, str]] = []

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

        valid.append((product, sale_date, int(qty_dec), price, str(row.get("seller_name") or "").strip()[:255]))

    if not valid:
        return {
            "batch_id": None, "created": 0, "units": 0, "revenue": Decimal("0"),
            "period_start": None, "period_end": None, "products": 0, "errors": errors,
        }

    start = min(v[1] for v in valid)
    end = max(v[1] for v in valid)

    # Same file uploaded twice? Compare against the history already stored for those days.
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
        incoming = Counter((p.id, d, q, pr) for p, d, q, pr, _ in valid)
        repeated = sum(min(c, existing[k]) for k, c in incoming.items())
        if repeated >= max(1, int(len(valid) * 0.9)):
            raise ConflictError(
                message="Estas ventas ya fueron importadas antes (mismas fechas, productos, cantidades y precios). "
                "No se volvieron a cargar para no duplicar tu historial."
            )

    batch = SalesBatchModel(
        company_id=company_id,
        source_file=f"Importación de ventas {datetime.now(LIMA):%d/%m/%Y %H:%M}",
        status="completed",
        row_count=len(valid),
        period_start=start,
        period_end=end,
    )
    session.add(batch)
    session.flush()

    units = 0
    revenue = Decimal("0")
    for product, sale_date, qty, price, seller in valid:
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
        "products": len({v[0].id for v in valid}),
        "errors": errors,
    }
