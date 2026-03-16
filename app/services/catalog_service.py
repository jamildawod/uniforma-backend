from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.schemas.product import (
    CatalogProductSummary,
    FilterOption,
    ProductListFilters,
    ProductListResponse,
    SearchMatch,
    SearchResponse,
)
from app.services.cache_service import CacheService
from app.services.category_tree_service import CategoryTreeService


class CatalogService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        cache_service: CacheService,
        category_tree_service: CategoryTreeService,
    ) -> None:
        self.session = session
        self.settings = settings
        self.cache_service = cache_service
        self.category_tree_service = category_tree_service

    async def list_products(
        self,
        *,
        category: str | None,
        color: str | None,
        size: str | None,
        search: str | None,
        cursor: str | None,
        limit: int,
    ) -> ProductListResponse:
        normalized_limit = limit or self.settings.catalog_default_limit
        limit = max(1, min(normalized_limit, self.settings.catalog_max_limit))
        version = await self.cache_service.get_version("catalog")
        cache_key = self._cache_key(
            "catalog:products:",
            {
                "version": version,
                "category": category,
                "color": color,
                "size": size,
                "search": search,
                "cursor": cursor,
                "limit": limit,
            },
        )

        async def factory() -> dict[str, Any]:
            cursor_created, cursor_id = self._decode_cursor(cursor)
            rows = await self.session.execute(
                text(
                    """
                    SELECT
                        product_id,
                        slug,
                        name,
                        created_at,
                        category,
                        brand,
                        price,
                        primary_image,
                        colors,
                        sizes
                    FROM product_list_view
                    WHERE (:category IS NULL OR category = :category)
                      AND (:color IS NULL OR :color = ANY(colors))
                      AND (:size IS NULL OR :size = ANY(sizes))
                      AND (:search IS NULL OR name % :search)
                      AND (
                        :cursor_created IS NULL
                        OR created_at > CAST(:cursor_created AS timestamptz)
                        OR (
                          created_at = CAST(:cursor_created AS timestamptz)
                          AND product_id > CAST(:cursor_id AS uuid)
                        )
                      )
                    ORDER BY created_at ASC, product_id ASC
                    LIMIT :limit_plus_one
                    """
                ),
                {
                    "category": category,
                    "color": color,
                    "size": size,
                    "search": search,
                    "cursor_created": cursor_created,
                    "cursor_id": cursor_id,
                    "limit_plus_one": limit + 1,
                },
            )
            results = [self._row_to_catalog_product(row) for row in rows.mappings().all()]
            next_cursor = None
            if len(results) > limit:
                next_cursor = self._encode_cursor(
                    results[limit - 1].created_at.isoformat(),
                    str(results[limit - 1].product_id),
                )
                results = results[:limit]

            filters = await self._build_filters(category=category, color=color, size=size, search=search)
            return {
                "products": [item.model_dump(mode="json") for item in results],
                "next_cursor": next_cursor,
                "filters": filters.model_dump(mode="json"),
            }

        payload = await self.cache_service.get_or_set_json(cache_key, factory)
        return ProductListResponse.model_validate(payload)

    async def search_products(self, query: str, limit: int = 10) -> SearchResponse:
        normalized_limit = max(1, min(limit, 10))
        version = await self.cache_service.get_version("catalog")
        cache_key = self._cache_key("catalog:search:", {"version": version, "query": query, "limit": normalized_limit})

        async def factory() -> dict[str, Any]:
            rows = await self.session.execute(
                text(
                    """
                    SELECT
                        product_id,
                        slug,
                        name,
                        category,
                        brand,
                        primary_image,
                        price,
                        similarity(name, :query) AS score
                    FROM product_list_view
                    WHERE name % :query
                    ORDER BY score DESC, name ASC
                    LIMIT :limit
                    """
                ),
                {"query": query, "limit": normalized_limit},
            )
            items = [
                SearchMatch(
                    product_id=row.product_id,
                    slug=row.slug,
                    name=row.name,
                    category=row.category,
                    primary_image=row.primary_image,
                    price=row.price,
                    score=float(row.score or 0.0),
                ).model_dump(mode="json")
                for row in rows.mappings().all()
            ]
            return {"items": items}

        payload = await self.cache_service.get_or_set_json(cache_key, factory)
        return SearchResponse.model_validate(payload)

    async def list_categories(self) -> list[dict[str, Any]]:
        version = await self.cache_service.get_version("catalog")
        cache_key = f"catalog:{version}:categories:tree"

        async def factory() -> list[dict[str, Any]]:
            tree = await self.category_tree_service.build_tree()
            return [item.model_dump(mode="json") for item in tree]

        return await self.cache_service.get_or_set_json(cache_key, factory)

    async def list_filters(self) -> ProductListFilters:
        version = await self.cache_service.get_version("catalog")
        cache_key = f"catalog:{version}:filters:all"

        async def factory() -> dict[str, Any]:
            filters = await self._build_filters(category=None, color=None, size=None, search=None)
            return filters.model_dump(mode="json")

        payload = await self.cache_service.get_or_set_json(cache_key, factory)
        return ProductListFilters.model_validate(payload)

    async def refresh_materialized_view(self) -> None:
        populated = await self.session.execute(
            text(
                """
                SELECT ispopulated
                FROM pg_matviews
                WHERE schemaname = current_schema()
                  AND matviewname = 'product_list_view'
                """
            )
        )
        is_populated = populated.scalar_one_or_none()
        has_unique_index = await self.session.execute(
            text(
                """
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = current_schema()
                  AND tablename = 'product_list_view'
                  AND indexname = 'idx_product_list_view_product_id'
                """
            )
        )
        if is_populated and has_unique_index.scalar_one_or_none():
            await self.session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY product_list_view"))
        else:
            await self.session.execute(text("REFRESH MATERIALIZED VIEW product_list_view"))
        await self.session.commit()
        await self.cache_service.bump_version("catalog")

    async def _build_filters(
        self,
        *,
        category: str | None,
        color: str | None,
        size: str | None,
        search: str | None,
    ) -> ProductListFilters:
        categories_result = await self.session.execute(
            text(
                """
                SELECT category AS value, COUNT(*)::int AS count
                FROM product_list_view
                WHERE (:search IS NULL OR name % :search)
                GROUP BY category
                ORDER BY count DESC, category ASC
                """
            ),
            {"search": search},
        )
        colors_result = await self.session.execute(
            text(
                """
                SELECT color AS value, COUNT(*)::int AS count
                FROM product_list_view, unnest(colors) AS color
                WHERE (:category IS NULL OR category = :category)
                  AND (:size IS NULL OR :size = ANY(sizes))
                  AND (:search IS NULL OR name % :search)
                GROUP BY color
                ORDER BY count DESC, color ASC
                """
            ),
            {"category": category, "size": size, "search": search},
        )
        sizes_result = await self.session.execute(
            text(
                """
                SELECT size AS value, COUNT(*)::int AS count
                FROM product_list_view, unnest(sizes) AS size
                WHERE (:category IS NULL OR category = :category)
                  AND (:color IS NULL OR :color = ANY(colors))
                  AND (:search IS NULL OR name % :search)
                GROUP BY size
                ORDER BY count DESC, size ASC
                """
            ),
            {"category": category, "color": color, "search": search},
        )
        return ProductListFilters(
            categories=[FilterOption(value=row.value, count=row.count) for row in categories_result.mappings().all() if row.value],
            colors=[FilterOption(value=row.value, count=row.count) for row in colors_result.mappings().all() if row.value],
            sizes=[FilterOption(value=row.value, count=row.count) for row in sizes_result.mappings().all() if row.value],
        )

    def _cache_key(self, prefix: str, payload: dict[str, Any]) -> str:
        if prefix == "catalog:products:":
            return ":".join(
                [
                    "catalog",
                    str(payload.get("version") or 1),
                    "products",
                    str(payload.get("category") or ""),
                    str(payload.get("color") or ""),
                    str(payload.get("size") or ""),
                    str(payload.get("search") or ""),
                    str(payload.get("cursor") or ""),
                    str(payload.get("limit") or self.settings.catalog_default_limit),
                ]
            )
        if prefix == "catalog:search:":
            return ":".join(
                [
                    "catalog",
                    str(payload.get("version") or 1),
                    "search",
                    str(payload.get("query") or ""),
                    str(payload.get("limit") or 10),
                ]
            )
        return prefix + json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def _encode_cursor(self, created_at: str, product_id: str) -> str:
        normalized = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
        raw = f"{normalized}|{product_id}".encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii")

    def _decode_cursor(self, cursor: str | None) -> tuple[str | None, str | None]:
        if not cursor:
            return None, None
        padding = len(cursor) % 4
        if padding:
            cursor += "=" * (4 - padding)
        try:
            decoded = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
            created_at, product_id = decoded.split("|", 1)
            return created_at or None, product_id or None
        except Exception:
            return None, None

    def _row_to_catalog_product(self, row: Any) -> CatalogProductSummary:
        product_id = row.product_id if isinstance(row.product_id, UUID) else UUID(str(row.product_id))
        created_at = row.created_at if isinstance(row.created_at, datetime) else datetime.fromisoformat(str(row.created_at))
        colors = [value for value in row.colors or [] if value]
        sizes = [value for value in row.sizes or [] if value]
        price = row.price
        if price is not None and not isinstance(price, Decimal):
            price = Decimal(str(price))
        return CatalogProductSummary(
            product_id=product_id,
            slug=row.slug,
            name=row.name,
            created_at=created_at,
            category=row.category,
            brand=row.brand,
            price=price,
            primary_image=row.primary_image,
            colors=colors,
            sizes=sizes,
        )
