from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class IntelligenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def fetch_summary(self) -> dict[str, Any]:
        result = await self.session.execute(
            text(
                """
                WITH product_stats AS (
                    SELECT
                        COUNT(*) AS total_products,
                        COUNT(*) FILTER (WHERE is_active = true AND deleted_at IS NULL) AS active_products,
                        COUNT(*) FILTER (WHERE deleted_at IS NOT NULL) AS deleted_products
                    FROM products
                ),
                variant_stats AS (
                    SELECT COUNT(*) AS total_variants
                    FROM product_variants
                ),
                sync_stats AS (
                    SELECT
                        MAX(finished_at) FILTER (WHERE status = 'success') AS last_successful_sync_at,
                        COUNT(*) FILTER (WHERE status = 'running') AS running_syncs
                    FROM sync_runs
                ),
                override_stats AS (
                    SELECT COUNT(*) AS override_count
                    FROM admin_overrides
                )
                SELECT
                    product_stats.total_products,
                    product_stats.active_products,
                    product_stats.deleted_products,
                    variant_stats.total_variants,
                    sync_stats.last_successful_sync_at,
                    sync_stats.running_syncs,
                    override_stats.override_count
                FROM product_stats, variant_stats, sync_stats, override_stats
                """
            )
        )
        row = result.mappings().one()
        return dict(row)

    async def fetch_data_quality_counts(self) -> list[dict[str, Any]]:
        result = await self.session.execute(
            text(
                """
                SELECT metric_key, metric_count
                FROM (
                    SELECT 'missing_brand' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM products
                    WHERE deleted_at IS NULL
                      AND (brand IS NULL OR BTRIM(brand) = '')

                    UNION ALL

                    SELECT 'missing_description' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM products
                    WHERE deleted_at IS NULL
                      AND (description IS NULL OR BTRIM(description) = '')

                    UNION ALL

                    SELECT 'variants_missing_ean' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM product_variants
                    WHERE deleted_at IS NULL
                      AND (ean IS NULL OR BTRIM(ean) = '')

                    UNION ALL

                    SELECT 'variants_zero_stock_active' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM product_variants
                    WHERE deleted_at IS NULL
                      AND is_active = true
                      AND stock_quantity = 0

                    UNION ALL

                    SELECT 'products_without_images' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM products p
                    WHERE p.deleted_at IS NULL
                      AND NOT EXISTS (
                          SELECT 1
                          FROM product_images i
                          WHERE i.product_id = p.id
                      )

                    UNION ALL

                    SELECT 'orphan_images' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM product_images i
                    LEFT JOIN products p ON p.id = i.product_id
                    LEFT JOIN product_variants v ON v.id = i.variant_id
                    WHERE p.id IS NULL
                       OR (i.variant_id IS NOT NULL AND v.id IS NULL)

                    UNION ALL

                    SELECT 'overrides_on_deleted_products' AS metric_key, COUNT(*)::bigint AS metric_count
                    FROM admin_overrides ao
                    INNER JOIN products p ON p.id = ao.product_id
                    WHERE p.deleted_at IS NOT NULL
                ) metrics
                ORDER BY metric_key
                """
            )
        )
        return [dict(row) for row in result.mappings().all()]

    async def fetch_sync_health(self, page: int, page_size: int) -> dict[str, Any]:
        offset = (page - 1) * page_size
        summary_result = await self.session.execute(
            text(
                """
                WITH last_completed_run AS (
                    SELECT started_at, finished_at
                    FROM sync_runs
                    WHERE finished_at IS NOT NULL
                    ORDER BY started_at DESC
                    LIMIT 1
                )
                SELECT
                    COUNT(*) FILTER (WHERE status = 'running')::bigint AS running_syncs,
                    MAX(finished_at) FILTER (WHERE status = 'success') AS last_successful_sync_at,
                    COUNT(*) FILTER (
                        WHERE status = 'failed'
                          AND started_at >= NOW() - INTERVAL '24 hours'
                    )::bigint AS failed_runs_last_24h,
                    AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) FILTER (
                        WHERE finished_at IS NOT NULL
                    ) AS average_duration_seconds,
                    MAX(started_at) FILTER (WHERE status = 'failed') AS last_failed_sync_at,
                    (
                        SELECT COUNT(*)::bigint
                        FROM products p, last_completed_run r
                        WHERE p.deleted_at IS NOT NULL
                          AND p.deleted_at >= r.started_at
                          AND p.deleted_at <= COALESCE(r.finished_at, NOW())
                    ) AS soft_deleted_products_last_run,
                    (
                        SELECT COUNT(*)::bigint
                        FROM product_variants v, last_completed_run r
                        WHERE v.deleted_at IS NOT NULL
                          AND v.deleted_at >= r.started_at
                          AND v.deleted_at <= COALESCE(r.finished_at, NOW())
                    ) AS soft_deleted_variants_last_run,
                    COUNT(*)::bigint AS total
                FROM sync_runs
                """
            )
        )
        recent_runs_result = await self.session.execute(
            text(
                """
                SELECT
                    id,
                    started_at,
                    finished_at,
                    status,
                    EXTRACT(EPOCH FROM (finished_at - started_at)) AS duration_seconds,
                    products_created,
                    products_updated,
                    variants_created,
                    variants_updated,
                    images_synced,
                    error_message
                FROM sync_runs
                ORDER BY started_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {
                "limit": page_size,
                "offset": offset,
            },
        )
        return {
            "summary": dict(summary_result.mappings().one()),
            "recent_runs": [dict(row) for row in recent_runs_result.mappings().all()],
        }

    async def fetch_override_conflicts(self, page: int, page_size: int) -> dict[str, Any]:
        offset = (page - 1) * page_size
        base_query = """
            WITH normalized_overrides AS (
                SELECT
                    ao.id::text AS id,
                    ao.product_id::text AS product_id,
                    p.name AS product_name,
                    ao.field_name,
                    CASE ao.field_name
                        WHEN 'name' THEN p.name
                        WHEN 'description' THEN p.description
                        WHEN 'brand' THEN p.brand
                        ELSE NULL
                    END AS source_value,
                    CASE
                        WHEN jsonb_typeof(ao.override_value) = 'string' THEN TRIM(BOTH '"' FROM ao.override_value::text)
                        WHEN ao.override_value IS NULL THEN NULL
                        ELSE ao.override_value::text
                    END AS override_value,
                    p.deleted_at,
                    p.updated_at AS product_updated_at,
                    ao.updated_at
                FROM admin_overrides ao
                INNER JOIN products p ON p.id = ao.product_id
                WHERE ao.field_name IN ('name', 'description', 'brand')
            ),
            conflicts AS (
                SELECT
                    id,
                    product_id,
                    product_name,
                    field_name,
                    source_value,
                    override_value,
                    COALESCE(override_value, source_value) AS final_value,
                    CASE
                        WHEN deleted_at IS NOT NULL THEN 'critical'
                        WHEN override_value IS NOT DISTINCT FROM source_value THEN 'warning'
                        WHEN product_updated_at IS NOT NULL
                             AND updated_at < product_updated_at
                             AND override_value IS DISTINCT FROM source_value THEN 'warning'
                        ELSE 'healthy'
                    END AS severity,
                    updated_at
                FROM normalized_overrides
                WHERE deleted_at IS NOT NULL
                   OR override_value IS NOT DISTINCT FROM source_value
                   OR (
                        product_updated_at IS NOT NULL
                        AND updated_at < product_updated_at
                        AND override_value IS DISTINCT FROM source_value
                   )
            )
        """
        total_result = await self.session.execute(text(f"{base_query} SELECT COUNT(*)::bigint AS total FROM conflicts"))
        rows_result = await self.session.execute(
            text(
                f"""
                {base_query}
                SELECT
                    id,
                    product_id,
                    product_name,
                    field_name,
                    source_value,
                    override_value,
                    final_value,
                    severity,
                    updated_at
                FROM conflicts
                ORDER BY updated_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {
                "limit": min(page_size, 100),
                "offset": offset,
            },
        )
        return {
            "total": int(total_result.scalar_one()),
            "conflicts": [dict(row) for row in rows_result.mappings().all()],
        }

    async def validate_index_names(self) -> set[str]:
        result = await self.session.execute(
            text(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                """
            )
        )
        return {str(row[0]) for row in result.all()}
