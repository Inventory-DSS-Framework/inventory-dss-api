"""Data preparation — pipeline use case: prepare a dataset from an ingestion batch."""
from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from app.modules.data_preparation.application.dtos import PreparedDatasetDTO
from app.modules.data_preparation.domain.entities import (
    PreparedDataset,
    PreparedTimeSeries,
)
from app.modules.data_preparation.domain.enums import DatasetStatus
from app.modules.data_preparation.domain.exceptions import InvalidDatasetError
from app.modules.data_preparation.domain.repositories import (
    PreparedDatasetRepository,
)
from app.modules.data_preparation.domain.services import prepare_demand_series
from app.modules.data_preparation.domain.value_objects import DemandRecord
from app.modules.data_preparation.infrastructure.file_parser import parse_demand_rows
from app.modules.ingestion.domain.exceptions import IngestionBatchNotFoundError
from app.modules.ingestion.domain.repositories import IngestionBatchRepository
from app.modules.products.domain.repositories import ProductRepository
from app.shared.domain.value_objects import DateRange
from app.shared.infrastructure.ports import StoragePort


class PrepareDatasetFromBatch:
    def __init__(
        self,
        *,
        batches: IngestionBatchRepository,
        products: ProductRepository,
        datasets: PreparedDatasetRepository,
        storage: StoragePort,
    ) -> None:
        self._batches = batches
        self._products = products
        self._datasets = datasets
        self._storage = storage

    def execute(
        self,
        company_id: UUID,
        *,
        batch_id: UUID,
        treat_zero_as_stockout: bool = False,
    ) -> PreparedDatasetDTO:
        batch = self._batches.get_by_id(batch_id)
        if batch is None or batch.company_id != company_id:
            raise IngestionBatchNotFoundError(
                message=f"Ingestion batch '{batch_id}' not found"
            )

        content = self._storage.get(batch.file_path)
        raw_rows = parse_demand_rows(
            content=content,
            file_type=batch.file_type,
            column_mapping=batch.column_mapping,
        )

        # Resolve SKUs to product ids; unknown SKUs are skipped.
        records: list[DemandRecord] = []
        for row in raw_rows:
            product = self._products.get_by_sku(company_id, row.sku)
            if product is None or product.id is None:
                continue
            records.append(
                DemandRecord(
                    product_id=product.id,
                    period_date=row.period_date,
                    quantity=row.quantity,
                    is_stockout=row.is_stockout,
                )
            )

        if not records:
            raise InvalidDatasetError(
                message="No rows could be prepared (no matching SKUs or empty file)."
            )

        prepared = prepare_demand_series(
            records, treat_zero_as_stockout=treat_zero_as_stockout
        )

        dataset_id = uuid4()
        series = [
            PreparedTimeSeries(
                dataset_id=dataset_id,
                product_id=p.product_id,
                points=p.points,
                has_stockout_flags=p.has_stockout_flags,
                outliers_treated=p.outliers_treated,
            )
            for p in prepared
        ]

        all_dates: list[date] = [pt.period_date for s in series for pt in s.points]
        period = DateRange(min(all_dates), max(all_dates)) if all_dates else None

        dataset = PreparedDataset(
            id=dataset_id,
            company_id=company_id,
            source_batch_id=batch_id,
            status=DatasetStatus.READY,
            product_count=len(series),
            period=period,
            series=series,
        )
        return PreparedDatasetDTO.from_entity(self._datasets.add(dataset))
