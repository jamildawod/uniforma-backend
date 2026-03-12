from datetime import UTC, datetime

from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger
from app.repositories.intelligence_repository import IntelligenceRepository
from app.schemas.intelligence import (
    DataQualityMetric,
    DataQualityResponse,
    OverrideConflict,
    OverrideConflictResponse,
    SyncHealthResponse,
    SyncRun,
    SystemHealthResponse,
)


class AdminIntelligenceService:
    def __init__(self, repository: IntelligenceRepository) -> None:
        self.repository = repository
        self.logger = get_logger(self.__class__.__name__)

    async def get_system_health(self) -> SystemHealthResponse:
        generated_at = datetime.now(UTC)
        try:
            payload = await self.repository.fetch_summary()
            running_syncs = int(payload["running_syncs"] or 0)
            last_successful_sync_at = payload["last_successful_sync_at"]
            deleted_products = int(payload["deleted_products"] or 0)

            status = "healthy"
            if last_successful_sync_at is None:
                status = "critical"
            elif running_syncs > 0 or deleted_products > 0:
                status = "warning"

            return SystemHealthResponse(
                status=status,
                generated_at=generated_at,
                total_products=int(payload["total_products"] or 0),
                active_products=int(payload["active_products"] or 0),
                deleted_products=deleted_products,
                total_variants=int(payload["total_variants"] or 0),
                last_successful_sync_at=last_successful_sync_at,
                running_syncs=running_syncs,
                override_count=int(payload["override_count"] or 0),
            )
        except SQLAlchemyError as exc:
            self.logger.error(
                "Failed to fetch intelligence summary",
                extra={"event": "intelligence_summary_failed", "error": str(exc)},
            )
            return SystemHealthResponse(status="unavailable", generated_at=generated_at)

    async def get_data_quality(self) -> DataQualityResponse:
        generated_at = datetime.now(UTC)
        try:
            rows = await self.repository.fetch_data_quality_counts()
            definitions = {
                "missing_brand": ("Products missing brand", "Missing brand from canonical product data.", "missing_brand"),
                "missing_description": (
                    "Products missing description",
                    "Missing long description from PIM source.",
                    "missing_description",
                ),
                "variants_missing_ean": (
                    "Variants missing EAN",
                    "Variants missing barcode/EAN values.",
                    "variants_missing_ean",
                ),
                "variants_zero_stock_active": (
                    "Active variants with zero stock",
                    "Sellable variants that currently report zero stock.",
                    "variants_zero_stock_active",
                ),
                "products_without_images": (
                    "Products without images",
                    "Products missing any linked product images.",
                    "products_without_images",
                ),
                "orphan_images": (
                    "Orphan images",
                    "Image rows without a valid parent product or variant.",
                    "orphan_images",
                ),
                "overrides_on_deleted_products": (
                    "Overrides on deleted products",
                    "Admin overrides attached to soft-deleted products.",
                    "overrides_on_deleted_products",
                ),
            }
            metrics: list[DataQualityMetric] = []
            for row in rows:
                key = str(row["metric_key"])
                count = int(row["metric_count"] or 0)
                label, description, filter_key = definitions[key]
                metrics.append(
                    DataQualityMetric(
                        key=key,
                        label=label,
                        count=count,
                        description=description,
                        filter=filter_key,
                        severity=self._metric_severity(key, count),
                    )
                )
            return DataQualityResponse(
                status="healthy",
                generated_at=generated_at,
                metrics=metrics,
            )
        except SQLAlchemyError as exc:
            self.logger.error(
                "Failed to fetch data quality metrics",
                extra={"event": "intelligence_data_quality_failed", "error": str(exc)},
            )
            return DataQualityResponse(status="unavailable", generated_at=generated_at)

    async def get_sync_health(self, page: int, page_size: int) -> SyncHealthResponse:
        generated_at = datetime.now(UTC)
        try:
            payload = await self.repository.fetch_sync_health(page=page, page_size=page_size)
            summary = payload["summary"]
            runs = [SyncRun(**row) for row in payload["recent_runs"]]

            status = "healthy"
            if int(summary["failed_runs_last_24h"] or 0) > 0:
                status = "warning"
            if int(summary["running_syncs"] or 0) > 1:
                status = "warning"

            return SyncHealthResponse(
                status=status,
                generated_at=generated_at,
                running_syncs=int(summary["running_syncs"] or 0),
                last_successful_sync_at=summary["last_successful_sync_at"],
                failed_runs_last_24h=int(summary["failed_runs_last_24h"] or 0),
                average_duration_seconds=float(summary["average_duration_seconds"])
                if summary["average_duration_seconds"] is not None
                else None,
                last_failed_sync_at=summary["last_failed_sync_at"],
                soft_deleted_products_last_run=int(summary["soft_deleted_products_last_run"] or 0),
                soft_deleted_variants_last_run=int(summary["soft_deleted_variants_last_run"] or 0),
                page=page,
                page_size=page_size,
                total=int(summary["total"] or 0),
                recent_runs=runs,
            )
        except SQLAlchemyError as exc:
            self.logger.error(
                "Failed to fetch sync health",
                extra={"event": "intelligence_sync_health_failed", "error": str(exc)},
            )
            return SyncHealthResponse(
                status="unavailable",
                generated_at=generated_at,
                page=page,
                page_size=page_size,
            )

    async def get_override_conflicts(self, page: int, page_size: int) -> OverrideConflictResponse:
        generated_at = datetime.now(UTC)
        try:
            payload = await self.repository.fetch_override_conflicts(page=page, page_size=page_size)
            return OverrideConflictResponse(
                status="healthy",
                generated_at=generated_at,
                page=page,
                page_size=page_size,
                total=int(payload["total"]),
                conflicts=[OverrideConflict(**row) for row in payload["conflicts"]],
            )
        except SQLAlchemyError as exc:
            self.logger.error(
                "Failed to fetch override conflicts",
                extra={"event": "intelligence_override_conflicts_failed", "error": str(exc)},
            )
            return OverrideConflictResponse(
                status="unavailable",
                generated_at=generated_at,
                page=page,
                page_size=page_size,
            )

    async def validate_indexes(self) -> list[str]:
        required_indexes = [
            "ix_products_deleted_at",
            "ix_products_brand",
            "ix_product_variants_ean",
            "ix_product_variants_stock_quantity",
            "ix_product_images_product_id",
            "ix_admin_overrides_product_id",
            "ix_sync_runs_started_at",
        ]
        existing_indexes = await self.repository.validate_index_names()
        return [index for index in required_indexes if index not in existing_indexes]

    def _metric_severity(self, key: str, count: int) -> str:
        if key == "variants_missing_ean":
            if count > 100:
                return "critical"
            if count > 20:
                return "warning"
            return "healthy"
        if key == "products_without_images":
            if count > 200:
                return "critical"
            if count > 50:
                return "warning"
            return "healthy"
        if count > 0:
            return "warning"
        return "healthy"
