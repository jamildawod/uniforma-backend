import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.attribute import Attribute
from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product, ProductStatus
from app.models.product_attribute_value import ProductAttributeValue
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _product_options(self) -> tuple:
        return (
            selectinload(Product.brand_rel),
            selectinload(Product.category),
            selectinload(Product.images),
            selectinload(Product.attribute_values).selectinload(ProductAttributeValue.attribute),
            selectinload(Product.variants).selectinload(ProductVariant.images),
        )

    async def list_products(self, limit: int = 50, offset: int = 0) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.deleted_at.is_(None))
            .options(*self._product_options())
            .order_by(Product.updated_at.desc(), Product.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def list_active_products(self, limit: int = 50, offset: int = 0) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.deleted_at.is_(None), Product.status == ProductStatus.active)
            .options(*self._product_options())
            .order_by(Product.updated_at.desc(), Product.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def search_products(self, query: str, limit: int = 50) -> list[Product]:
        pattern = f"%{query.strip()}%"
        statement = (
            select(Product)
            .where(
                Product.deleted_at.is_(None),
                Product.status == ProductStatus.active,
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                    Product.slug.ilike(pattern),
                ),
            )
            .options(*self._product_options())
            .order_by(Product.name.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def get_product_by_slug(self, slug: str) -> Product | None:
        statement = (
            select(Product)
            .where(Product.slug == slug, Product.status == ProductStatus.active, Product.deleted_at.is_(None))
            .options(*self._product_options())
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_any_product_by_slug(self, slug: str) -> Product | None:
        statement = select(Product).where(Product.slug == slug).options(*self._product_options())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_product_by_id(self, product_id: uuid.UUID) -> Product | None:
        statement = select(Product).where(Product.id == product_id).options(*self._product_options())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_product_by_identifier(self, identifier: str) -> Product | None:
        try:
            product_id = uuid.UUID(identifier)
        except ValueError:
            return await self.get_product_by_slug(identifier)
        return await self.get_product_by_id(product_id)

    async def get_product_variant(self, variant_id: int) -> ProductVariant | None:
        result = await self.session.execute(
            select(ProductVariant)
            .where(ProductVariant.id == variant_id)
            .options(selectinload(ProductVariant.images))
        )
        return result.scalar_one_or_none()

    async def list_product_variants(self, product_id: uuid.UUID) -> list[ProductVariant]:
        result = await self.session.execute(
            select(ProductVariant)
            .where(ProductVariant.product_id == product_id, ProductVariant.deleted_at.is_(None))
            .options(selectinload(ProductVariant.images))
            .order_by(ProductVariant.created_at.asc(), ProductVariant.id.asc())
        )
        return list(result.scalars().unique().all())

    async def list_product_images(self, product_id: uuid.UUID) -> list[ProductImage]:
        result = await self.session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.position.asc(), ProductImage.id.asc())
        )
        return list(result.scalars().all())

    async def list_brands(self) -> list[Brand]:
        result = await self.session.execute(select(Brand).order_by(Brand.name.asc()))
        return list(result.scalars().all())

    async def get_brand_by_id(self, brand_id: int) -> Brand | None:
        result = await self.session.execute(select(Brand).where(Brand.id == brand_id))
        return result.scalar_one_or_none()

    async def get_brand_by_slug(self, slug: str) -> Brand | None:
        result = await self.session.execute(select(Brand).where(Brand.slug == slug))
        return result.scalar_one_or_none()

    async def add_brand(self, brand: Brand) -> Brand:
        self.session.add(brand)
        await self.session.flush()
        return brand

    async def list_categories(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.position.asc(), Category.name.asc()))
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: int) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_category_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def get_categories_by_slugs(self, slugs: list[str]) -> dict[str, Category]:
        if not slugs:
            return {}
        result = await self.session.execute(select(Category).where(Category.slug.in_(slugs)))
        categories = result.scalars().all()
        return {category.slug: category for category in categories}

    async def add_category(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category

    async def list_attributes(self) -> list[Attribute]:
        result = await self.session.execute(select(Attribute).order_by(Attribute.name.asc()))
        return list(result.scalars().all())

    async def get_attribute_by_id(self, attribute_id: int) -> Attribute | None:
        result = await self.session.execute(select(Attribute).where(Attribute.id == attribute_id))
        return result.scalar_one_or_none()

    async def get_attribute_by_name(self, name: str) -> Attribute | None:
        result = await self.session.execute(select(Attribute).where(Attribute.name == name))
        return result.scalar_one_or_none()

    async def add_attribute(self, attribute: Attribute) -> Attribute:
        self.session.add(attribute)
        await self.session.flush()
        return attribute

    async def add_attribute_value(self, attribute_value: ProductAttributeValue) -> ProductAttributeValue:
        self.session.add(attribute_value)
        await self.session.flush()
        return attribute_value

    async def delete_product_attribute_values(self, product_id: uuid.UUID) -> None:
        product = await self.get_product_by_id(product_id)
        if product is None:
            return
        for attribute_value in list(product.attribute_values):
            await self.session.delete(attribute_value)
        await self.session.flush()

    async def get_by_external_ids(self, external_ids: list[str]) -> dict[str, Product]:
        if not external_ids:
            return {}
        result = await self.session.execute(select(Product).where(Product.external_id.in_(external_ids)))
        products = result.scalars().all()
        return {product.external_id: product for product in products}

    async def get_by_skus(self, skus: list[str]) -> dict[str, ProductVariant]:
        if not skus:
            return {}
        result = await self.session.execute(select(ProductVariant).where(ProductVariant.sku.in_(skus)))
        variants = result.scalars().all()
        return {variant.sku: variant for variant in variants}

    async def get_images_by_external_paths(self, external_paths: list[str]) -> dict[str, ProductImage]:
        if not external_paths:
            return {}
        result = await self.session.execute(select(ProductImage).where(ProductImage.external_path.in_(external_paths)))
        images = result.scalars().all()
        return {image.external_path: image for image in images}

    async def list_images_needing_sync(self) -> list[ProductImage]:
        result = await self.session.execute(select(ProductImage).where(ProductImage.external_path.is_not(None)))
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
                status=ProductStatus.archived,
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

    async def count_products(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Product).where(Product.deleted_at.is_(None)))
        return int(result.scalar_one())

    async def count_variants(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(ProductVariant))
        return int(result.scalar_one())

    async def add_product(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product

    async def update_product(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product

    async def soft_delete_product(self, product: Product) -> Product:
        product.deleted_at = datetime.now(timezone.utc)
        product.is_active = False
        product.status = ProductStatus.archived
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
