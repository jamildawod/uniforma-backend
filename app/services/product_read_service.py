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
    ProductImageRead,
    ProductRead,
    ProductVariantRead,
)

ALLOWED_OVERRIDE_FIELDS = {
    "name",
    "description",
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

    async def search_public_products(self, query: str, limit: int = 50) -> list[ProductRead]:
        products = await self.product_repository.search_products(query=query, limit=limit)
        override_map = await self.admin_override_repository.list_by_product_ids([product.id for product in products])
        return [self._merge_product(product, override_map.get(product.id, [])) for product in products]

    async def get_public_product(self, identifier: str) -> ProductRead | None:
        product = await self.product_repository.get_product_by_identifier(identifier)
        if product is None or product.deleted_at is not None or self._status_value(product) != "active":
            return None
        overrides = await self.admin_override_repository.list_by_product_ids([product.id])
        return self._merge_product(product, overrides.get(product.id, []))

    async def get_public_variants(self, identifier: str) -> list[ProductVariantRead] | None:
        product = await self.product_repository.get_product_by_identifier(identifier)
        if product is None or product.deleted_at is not None or self._status_value(product) != "active":
            return None
        return [ProductVariantRead.model_validate(variant) for variant in product.variants if variant.is_active]

    async def get_public_images(self, identifier: str) -> list[ProductImageRead] | None:
        product = await self.product_repository.get_product_by_identifier(identifier)
        if product is None or product.deleted_at is not None or self._status_value(product) != "active":
            return None
        return [ProductImageRead.model_validate(image) for image in sorted(product.images, key=lambda image: (image.position, image.id))]

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
            external_path=payload.url,
            url=payload.url,
            local_path=payload.url if payload.url.startswith("/uploads/") else None,
            is_primary=payload.is_primary,
            sort_order=payload.position,
            position=payload.position,
        )
        try:
            await self.product_repository.add_image(image)
        except IntegrityError as exc:
            await self.product_repository.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Image with this url already exists.",
            ) from exc

        refreshed = await self.product_repository.get_product_by_id(product_id)
        override_map = await self.admin_override_repository.list_by_product_ids([product_id])
        return self._merge_admin_product(refreshed, override_map.get(product_id, []))

    def _merge_product(self, product: Product, overrides: list[AdminOverride]) -> ProductRead:
        merged = ProductRead.model_validate(
            {
                "id": product.id,
                "external_id": product.external_id,
                "name": product.name,
                "slug": product.slug,
                "description": product.description,
                "status": product.status.value if hasattr(product.status, "value") else product.status,
                "brand_id": product.brand_id,
                "brand": product.brand_rel,
                "category_id": product.category_id,
                "category": product.category,
                "image_url": self._resolve_image_url(product),
                "is_active": product.is_active,
                "deleted_at": product.deleted_at,
                "last_seen_at": product.last_seen_at,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "images": [ProductImageRead.model_validate(image) for image in sorted(product.images, key=lambda item: (item.position, item.id))],
                "variants": [ProductVariantRead.model_validate(variant) for variant in product.variants if variant.deleted_at is None],
                "attributes": [
                    {
                        "attribute_id": value.attribute_id,
                        "value": value.value,
                        "attribute": value.attribute,
                    }
                    for value in product.attribute_values
                ],
            }
        ).model_dump()
        applied_overrides = self._filter_overrides(overrides)
        for field_name, override_value in applied_overrides.items():
            if field_name in {"name", "description"}:
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
        return {
            override.field_name: override.override_value
            for override in overrides
            if override.field_name in ALLOWED_OVERRIDE_FIELDS
        }

    def _resolve_image_url(self, product: Product) -> str | None:
        ordered_images = sorted(product.images, key=lambda image: (not image.is_primary, image.position, image.id))
        if not ordered_images:
            return None
        image = ordered_images[0]
        return image.url or image.local_path or image.external_path

    def _status_value(self, product: Product) -> str:
        return product.status.value if hasattr(product.status, "value") else str(product.status)
