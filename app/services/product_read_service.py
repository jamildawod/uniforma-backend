import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.logging import get_logger
from app.models.admin_override import AdminOverride
from app.models.product import Product
from app.models.product_image import ProductImage
from app.repositories.admin_override_repository import AdminOverrideRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    AdminImageCreateRequest,
    AdminProductRead,
    AdminOverridePatchRequest,
    ProductRead,
    ProductVariantRead,
)

ALLOWED_OVERRIDE_FIELDS = {
    "name",
    "description",
    "brand",
}


class ProductReadService:
    def __init__(
        self,
        product_repository: ProductRepository,
        admin_override_repository: AdminOverrideRepository,
    ) -> None:
        self.product_repository = product_repository
        self.admin_override_repository = admin_override_repository
        self.logger = get_logger(self.__class__.__name__)

    async def list_public_products(self, limit: int = 50, offset: int = 0) -> list[ProductRead]:
        products = await self.product_repository.list_active_products(limit=limit, offset=offset)
        override_map = await self.admin_override_repository.list_by_product_ids([product.id for product in products])
        return [self._merge_product(product, override_map.get(product.id, [])) for product in products]

    async def get_public_product(self, slug: str) -> ProductRead | None:
        product = await self.product_repository.get_product_by_slug(slug)
        if product is None:
            return None
        overrides = await self.admin_override_repository.list_by_product_ids([product.id])
        return self._merge_product(product, overrides.get(product.id, []))

    async def get_public_variants(self, slug: str) -> list[ProductVariantRead] | None:
        product = await self.product_repository.get_product_by_slug(slug)
        if product is None:
            return None
        return [ProductVariantRead.model_validate(variant) for variant in product.variants if variant.is_active]

    async def list_admin_products(self, limit: int = 50, offset: int = 0) -> list[AdminProductRead]:
        products = await self.product_repository.list_products(limit=limit, offset=offset)
        override_map = await self.admin_override_repository.list_by_product_ids([product.id for product in products])
        return [self._merge_admin_product(product, override_map.get(product.id, [])) for product in products]

    async def get_admin_product(self, product_id: uuid.UUID) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None
        override_map = await self.admin_override_repository.list_by_product_ids([product.id])
        return self._merge_admin_product(product, override_map.get(product.id, []))

    async def patch_admin_product(
        self,
        product_id: uuid.UUID,
        payload: AdminOverridePatchRequest,
        updated_by: str,
    ) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None

        for field_name, override_value in payload.overrides.items():
            if field_name not in ALLOWED_OVERRIDE_FIELDS:
                self.logger.warning(
                    "Rejected disallowed override field '%s' for product %s",
                    field_name,
                    product_id,
                )
                continue
            override = await self.admin_override_repository.get_by_product_and_field(product_id, field_name)
            if override is None:
                override = AdminOverride(
                    product_id=product_id,
                    field_name=field_name,
                    override_value=override_value,
                    updated_by=updated_by,
                )
                await self.admin_override_repository.add(override)
            else:
                override.override_value = override_value
                override.updated_by = updated_by

        override_map = await self.admin_override_repository.list_by_product_ids([product.id])
        return self._merge_admin_product(product, override_map.get(product.id, []))

    async def add_product_image(
        self,
        product_id: uuid.UUID,
        payload: AdminImageCreateRequest,
    ) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None

        image = ProductImage(
            product_id=product_id,
            variant_id=payload.variant_id,
            external_path=payload.external_path,
            local_path=payload.local_path,
            is_primary=payload.is_primary,
            sort_order=payload.sort_order,
        )
        try:
            await self.product_repository.add_image(image)
        except IntegrityError as exc:
            session = self.product_repository.session
            await session.rollback()
            self.logger.warning(
                "Rejected duplicate product image for external_path '%s'",
                payload.external_path,
                extra={
                    "event": "admin_product_image_integrity_error",
                    "product_id": str(product_id),
                    "external_path": payload.external_path,
                    "error": str(exc),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Image with this external_path already exists.",
            ) from exc
        refreshed = await self.product_repository.get_product_by_id(product_id)
        override_map = await self.admin_override_repository.list_by_product_ids([product_id])
        return self._merge_admin_product(refreshed, override_map.get(product_id, []))

    def _merge_product(self, product: Product, overrides: list[AdminOverride]) -> ProductRead:
        merged = ProductRead.model_validate(product).model_dump()
        applied_overrides = self._filter_overrides(overrides)
        for field_name, override_value in applied_overrides.items():
            if field_name in merged:
                merged[field_name] = override_value
        return ProductRead.model_validate(merged)

    def _merge_admin_product(self, product: Product, overrides: list[AdminOverride]) -> AdminProductRead:
        merged = self._merge_product(product, overrides).model_dump()
        merged["applied_overrides"] = self._filter_overrides(overrides)
        return AdminProductRead.model_validate(merged)

    def _filter_overrides(
        self,
        overrides: list[AdminOverride],
    ) -> dict[str, str | int | float | bool | list | dict | None]:
        filtered: dict[str, str | int | float | bool | list | dict | None] = {}
        for override in overrides:
            if override.field_name not in ALLOWED_OVERRIDE_FIELDS:
                self.logger.warning(
                    "Ignored disallowed override field '%s' for product %s",
                    override.field_name,
                    override.product_id,
                )
                continue
            filtered[override.field_name] = override.override_value
        return filtered
