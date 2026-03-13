import hashlib
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.text import slugify
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.repositories.admin_override_repository import AdminOverrideRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    AdminImageCreateRequest,
    AdminProductCreateRequest,
    AdminProductRead,
    AdminProductUpdateRequest,
    ProductRead,
)
from app.services.product_read_service import ProductReadService


class ProductService(ProductReadService):
    def __init__(
        self,
        product_repository: ProductRepository,
        admin_override_repository: AdminOverrideRepository,
    ) -> None:
        super().__init__(product_repository, admin_override_repository)

    async def create_admin_product(
        self,
        payload: AdminProductCreateRequest,
    ) -> AdminProductRead:
        slug = await self._ensure_unique_slug(payload.slug or payload.name)
        category = await self._resolve_category(payload.category)
        external_id = f"manual-{uuid.uuid4()}"
        source_hash = hashlib.sha256(f"{external_id}:{slug}:{payload.name}".encode("utf-8")).hexdigest()
        product = Product(
            external_id=external_id,
            source_hash=source_hash,
            name=payload.name,
            slug=slug,
            description=payload.description,
            brand=payload.brand,
            category_id=category.id if category else None,
            is_active=payload.is_active,
            last_seen_at=datetime.now(timezone.utc),
        )
        await self.product_repository.add_product(product)
        if payload.image_url:
            await self._upsert_primary_image(product.id, payload.image_url)
        return await self._load_admin_product_or_404(product.id)

    async def update_admin_product(
        self,
        product_id: uuid.UUID,
        payload: AdminProductUpdateRequest,
    ) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None

        candidate_slug = payload.slug or payload.name
        if product.slug != candidate_slug:
            product.slug = await self._ensure_unique_slug(candidate_slug, current_product_id=product.id)
        category = await self._resolve_category(payload.category)
        product.name = payload.name
        product.description = payload.description
        product.brand = payload.brand
        product.category_id = category.id if category else None
        product.is_active = payload.is_active
        await self.product_repository.update_product(product)
        if payload.image_url is not None:
            await self._upsert_primary_image(product.id, payload.image_url)
        return await self._load_admin_product_or_404(product.id)

    async def delete_admin_product(self, product_id: uuid.UUID) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None
        await self.product_repository.soft_delete_product(product)
        return await self._load_admin_product_or_404(product_id)

    async def set_product_publication(self, product_id: uuid.UUID, is_active: bool) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None
        product.is_active = is_active
        await self.product_repository.update_product(product)
        return await self._load_admin_product_or_404(product_id)

    async def get_public_product_by_identifier(self, identifier: str) -> ProductRead | None:
        product = await self.product_repository.get_product_by_identifier(identifier)
        if product is None or product.deleted_at is not None or not product.is_active:
            return None
        overrides = await self.admin_override_repository.list_by_product_ids([product.id])
        return self._merge_product(product, overrides.get(product.id, []))

    async def _ensure_unique_slug(self, source: str, current_product_id: uuid.UUID | None = None) -> str:
        base_slug = slugify(source)
        slug = base_slug
        counter = 2
        while True:
            existing_product = await self.product_repository.get_any_product_by_slug(slug)
            if existing_product is None or existing_product.id == current_product_id:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    async def _resolve_category(self, category_name: str | None) -> Category | None:
        if not category_name:
            return None
        category_slug = slugify(category_name)
        category = await self.product_repository.get_category_by_slug(category_slug)
        if category is not None:
            return category
        category = Category(name=category_name, slug=category_slug)
        return await self.product_repository.add_category(category)

    async def _upsert_primary_image(self, product_id: uuid.UUID, image_url: str) -> None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return
        primary_image = next((image for image in product.images if image.is_primary), None)
        if not image_url.strip():
            if primary_image is not None:
                primary_image.is_primary = False
                await self.product_repository.update_product(product)
            return
        if primary_image is None:
            try:
                await self.product_repository.add_image(
                    ProductImage(
                        product_id=product_id,
                        external_path=image_url,
                        local_path=image_url if image_url.startswith("/uploads/") else None,
                        is_primary=True,
                        sort_order=0,
                    )
                )
            except IntegrityError as exc:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Image already exists for another product.",
                ) from exc
            return

        primary_image.external_path = image_url
        primary_image.local_path = image_url if image_url.startswith("/uploads/") else None
        primary_image.is_primary = True
        await self.product_repository.update_product(product)

    async def add_uploaded_image(
        self,
        product_id: uuid.UUID,
        image_url: str,
    ) -> AdminProductRead | None:
        payload = AdminImageCreateRequest(
            external_path=image_url,
            local_path=image_url,
            is_primary=False,
            sort_order=0,
        )
        return await self.add_product_image(product_id, payload)

    async def _load_admin_product_or_404(self, product_id: uuid.UUID) -> AdminProductRead:
        product = await self.get_admin_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        return product
