import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.text import slugify
from app.models.brand import Brand
from app.models.category import Category
from app.models.attribute import Attribute, AttributeType
from app.models.product import Product, ProductStatus
from app.models.product_attribute_value import ProductAttributeValue
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.repositories.admin_override_repository import AdminOverrideRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    AdminImageCreateRequest,
    AdminProductCreateRequest,
    AdminProductRead,
    AdminProductUpdateRequest,
    AdminVariantCreateRequest,
    AttributeCreateRequest,
    AttributeRead,
    BrandCreateRequest,
    BrandRead,
    CategoryCreateRequest,
    CategoryRead,
    MediaItemRead,
)
from app.services.product_read_service import ProductReadService


class ProductService(ProductReadService):
    def __init__(
        self,
        product_repository: ProductRepository,
        admin_override_repository: AdminOverrideRepository,
    ) -> None:
        super().__init__(product_repository, admin_override_repository)

    async def create_admin_product(self, payload: AdminProductCreateRequest) -> AdminProductRead:
        slug = await self._ensure_unique_slug(payload.slug or payload.name)
        product = Product(
            external_id=f"manual-{uuid.uuid4()}",
            source_hash=hashlib.sha256(f"{slug}:{payload.name}".encode("utf-8")).hexdigest(),
            name=payload.name,
            slug=slug,
            description=payload.description,
            brand=(await self._resolve_brand_name(payload.brand_id)),
            brand_id=payload.brand_id,
            category_id=payload.category_id,
            status=ProductStatus(payload.status),
            is_active=payload.is_active,
            last_seen_at=datetime.now(timezone.utc),
        )
        await self.product_repository.add_product(product)
        await self._replace_attributes(product.id, payload.attributes)
        for variant_payload in payload.variants:
            await self._create_variant(product.id, variant_payload)
        if payload.image_url:
            await self.add_product_image(
                product.id,
                AdminImageCreateRequest(url=payload.image_url, is_primary=True, position=0),
            )
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
        product.name = payload.name
        product.description = payload.description
        product.brand = await self._resolve_brand_name(payload.brand_id)
        product.brand_id = payload.brand_id
        product.category_id = payload.category_id
        product.status = ProductStatus(payload.status)
        product.is_active = payload.is_active
        await self.product_repository.update_product(product)
        await self._replace_attributes(product.id, payload.attributes)
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
        if is_active and product.status == ProductStatus.draft:
            product.status = ProductStatus.active
        if not is_active and product.status == ProductStatus.active:
            product.status = ProductStatus.draft
        await self.product_repository.update_product(product)
        return await self._load_admin_product_or_404(product_id)

    async def create_variant(self, product_id: uuid.UUID, payload: AdminVariantCreateRequest) -> AdminProductRead | None:
        product = await self.product_repository.get_product_by_id(product_id)
        if product is None:
            return None
        await self._create_variant(product_id, payload)
        return await self._load_admin_product_or_404(product_id)

    async def add_product_gallery_image(self, product_id: uuid.UUID, payload: AdminImageCreateRequest) -> AdminProductRead | None:
        return await self.add_product_image(product_id, payload)

    async def list_brands(self) -> list[BrandRead]:
        return [BrandRead.model_validate(brand) for brand in await self.product_repository.list_brands()]

    async def create_brand(self, payload: BrandCreateRequest) -> BrandRead:
        slug = slugify(payload.slug or payload.name)
        existing = await self.product_repository.get_brand_by_slug(slug)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Brand slug already exists.")
        brand = Brand(name=payload.name, slug=slug, logo_url=payload.logo_url)
        created = await self.product_repository.add_brand(brand)
        return BrandRead.model_validate(created)

    async def list_categories(self) -> list[CategoryRead]:
        return [CategoryRead.model_validate(category) for category in await self.product_repository.list_categories()]

    async def create_category(self, payload: CategoryCreateRequest) -> CategoryRead:
        slug = slugify(payload.slug or payload.name)
        existing = await self.product_repository.get_category_by_slug(slug)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category slug already exists.")
        category = Category(name=payload.name, slug=slug, parent_id=payload.parent_id, position=payload.position)
        created = await self.product_repository.add_category(category)
        return CategoryRead.model_validate(created)

    async def list_media(self, uploads_root: Path) -> list[MediaItemRead]:
        uploads_root.mkdir(parents=True, exist_ok=True)
        items = []
        for path in sorted(uploads_root.iterdir(), key=lambda item: item.name.lower()):
            if path.is_file():
                items.append(MediaItemRead(filename=path.name, url=f"/uploads/{path.name}"))
        return items

    async def list_attributes(self) -> list[AttributeRead]:
        return [AttributeRead.model_validate(attribute) for attribute in await self.product_repository.list_attributes()]

    async def create_attribute(self, payload: AttributeCreateRequest) -> AttributeRead:
        existing = await self.product_repository.get_attribute_by_name(payload.name)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attribute already exists.")
        attribute = Attribute(name=payload.name, type=AttributeType(payload.type))
        created = await self.product_repository.add_attribute(attribute)
        return AttributeRead.model_validate(created)

    async def _replace_attributes(self, product_id: uuid.UUID, attributes: list) -> None:
        await self.product_repository.delete_product_attribute_values(product_id)
        for item in attributes:
            attribute = await self.product_repository.get_attribute_by_id(item.attribute_id)
            if attribute is None:
                continue
            await self.product_repository.add_attribute_value(
                ProductAttributeValue(product_id=product_id, attribute_id=item.attribute_id, value=item.value)
            )

    async def _resolve_brand_name(self, brand_id: int | None) -> str | None:
        if brand_id is None:
            return None
        brand = await self.product_repository.get_brand_by_id(brand_id)
        return brand.name if brand is not None else None

    async def _create_variant(self, product_id: uuid.UUID, payload: AdminVariantCreateRequest) -> ProductVariant:
        variant = ProductVariant(
            product_id=product_id,
            sku=payload.sku,
            source_hash=hashlib.sha256(f"{product_id}:{payload.sku}".encode("utf-8")).hexdigest(),
            ean=payload.ean,
            size=payload.size,
            color=payload.color,
            price=payload.price,
            currency="SEK" if payload.price is not None else None,
            stock_quantity=payload.stock_quantity,
            is_active=payload.is_active,
            last_seen_at=datetime.now(timezone.utc),
        )
        try:
            return await self.product_repository.add_variant(variant)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Variant SKU already exists.") from exc

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
            await self.add_product_image(
                product_id,
                AdminImageCreateRequest(url=image_url, is_primary=True, position=0),
            )
            return

        primary_image.external_path = image_url
        primary_image.url = image_url
        primary_image.local_path = image_url if image_url.startswith("/uploads/") else None
        primary_image.is_primary = True
        primary_image.position = 0
        primary_image.sort_order = 0
        await self.product_repository.update_product(product)

    async def _load_admin_product_or_404(self, product_id: uuid.UUID) -> AdminProductRead:
        product = await self.get_admin_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        return product
