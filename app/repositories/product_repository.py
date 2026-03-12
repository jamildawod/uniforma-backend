import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_products(self, limit: int = 50, offset: int = 0) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.deleted_at.is_(None))
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.variants).selectinload(ProductVariant.images),
            )
            .order_by(Product.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def list_active_products(self, limit: int = 50, offset: int = 0) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.is_active.is_(True), Product.deleted_at.is_(None))
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.variants).selectinload(ProductVariant.images),
            )
            .order_by(Product.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def get_product_by_slug(self, slug: str) -> Product | None:
        statement = (
            select(Product)
            .where(Product.slug == slug, Product.is_active.is_(True), Product.deleted_at.is_(None))
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.variants).selectinload(ProductVariant.images),
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_product_by_id(self, product_id: uuid.UUID) -> Product | None:
        statement = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.variants).selectinload(ProductVariant.images),
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_external_ids(self, external_ids: list[str]) -> dict[str, Product]:
        if not external_ids:
            return {}
        statement = select(Product).where(Product.external_id.in_(external_ids))
        result = await self.session.execute(statement)
        products = result.scalars().all()
        return {product.external_id: product for product in products}

    async def get_by_skus(self, skus: list[str]) -> dict[str, ProductVariant]:
        if not skus:
            return {}
        statement = select(ProductVariant).where(ProductVariant.sku.in_(skus))
        result = await self.session.execute(statement)
        variants = result.scalars().all()
        return {variant.sku: variant for variant in variants}

    async def get_categories_by_slugs(self, slugs: list[str]) -> dict[str, Category]:
        if not slugs:
            return {}
        statement = select(Category).where(Category.slug.in_(slugs))
        result = await self.session.execute(statement)
        categories = result.scalars().all()
        return {category.slug: category for category in categories}

    async def get_images_by_external_paths(self, external_paths: list[str]) -> dict[str, ProductImage]:
        if not external_paths:
            return {}
        statement = select(ProductImage).where(ProductImage.external_path.in_(external_paths))
        result = await self.session.execute(statement)
        images = result.scalars().all()
        return {image.external_path: image for image in images}

    async def list_images_needing_sync(self) -> list[ProductImage]:
        statement = select(ProductImage).where(ProductImage.external_path.is_not(None))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def soft_delete_missing_products(self, seen_at: datetime, deleted_at: datetime) -> None:
        statement = (
            update(Product)
            .where(
                (Product.last_seen_at.is_(None)) | (Product.last_seen_at < seen_at),
                Product.deleted_at.is_(None),
            )
            .values(
                deleted_at=deleted_at,
                is_active=False,
            )
        )
        await self.session.execute(statement)

    async def soft_delete_missing_variants(self, seen_at: datetime, deleted_at: datetime) -> None:
        statement = (
            update(ProductVariant)
            .where(
                (ProductVariant.last_seen_at.is_(None)) | (ProductVariant.last_seen_at < seen_at),
                ProductVariant.deleted_at.is_(None),
            )
            .values(
                deleted_at=deleted_at,
                is_active=False,
            )
        )
        await self.session.execute(statement)

    async def add_category(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category

    async def add_product(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product

    async def add_variant(self, variant: ProductVariant) -> ProductVariant:
        self.session.add(variant)
        await self.session.flush()
        return variant

    async def add_image(self, image: ProductImage) -> ProductImage:
        self.session.add(image)
        await self.session.flush()
        return image
