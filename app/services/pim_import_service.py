import hashlib
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.text import slugify
from app.models.attribute import Attribute, AttributeType
from app.models.brand import Brand
from app.models.category import Category
from app.models.pim_import_run import PimImportRun
from app.models.pim_source import PimSource, PimSourceType
from app.models.product import Product, ProductStatus
from app.models.product_attribute_value import ProductAttributeValue
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.repositories.pim_repository import PimRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.sync import PimSyncResponse
from app.services.pim_downloader import PimDownloader
from app.services.pim_parsers import CsvPimParser, JsonPimParser, XmlPimParser
from app.services.pim_parsers.common import NormalizedProduct


@dataclass(slots=True)
class ImportResult:
    processed: int = 0
    created: int = 0
    updated: int = 0
    sync: PimSyncResponse = field(default_factory=PimSyncResponse)


class PimImportService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        product_repository: ProductRepository,
        pim_repository: PimRepository,
        downloader: PimDownloader,
    ) -> None:
        self.session = session
        self.settings = settings
        self.product_repository = product_repository
        self.pim_repository = pim_repository
        self.downloader = downloader

    async def list_sources(self) -> list[PimSource]:
        return await self.pim_repository.list_sources()

    async def list_import_runs(self, limit: int = 50) -> list[PimImportRun]:
        return await self.pim_repository.list_import_runs(limit=limit)

    async def create_source(self, payload: dict) -> PimSource:
        payload["type"] = PimSourceType(payload["type"])
        source = PimSource(**payload)
        return await self.pim_repository.add_source(source)

    async def test_source_connection(self, source: PimSource) -> bool:
        path = await self.downloader.download(source)
        return path.exists()

    async def run_import(self, source: PimSource) -> ImportResult:
        lock_acquired = False
        advisory_lock_key = self._advisory_lock_key(source.id)
        import_run = PimImportRun(source_id=source.id, status="running", started_at=datetime.now(UTC))
        await self.pim_repository.add_import_run(import_run)

        try:
            result = await self.session.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": advisory_lock_key})
            lock_acquired = bool(result.scalar())
            if not lock_acquired:
                raise RuntimeError("Import already running for source")

            import_file = await self.downloader.download(source)
            products = self._parse(import_file)
            summary = await self._upsert_products(products, source)
            import_run.status = "success"
            import_run.finished_at = datetime.now(UTC)
            import_run.records_processed = summary.processed
            import_run.records_created = summary.created
            import_run.records_updated = summary.updated
            await self.session.commit()
            return summary
        except Exception as exc:
            await self.session.rollback()
            import_run.status = "failed"
            import_run.finished_at = datetime.now(UTC)
            import_run.error_log = str(exc)
            self.session.add(import_run)
            await self.session.commit()
            raise
        finally:
            if lock_acquired:
                await self.session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": advisory_lock_key})

    async def run_active_imports(self) -> list[ImportResult]:
        results: list[ImportResult] = []
        for source in await self.pim_repository.list_sources(active_only=True):
            results.append(await self.run_import(source))
        return results

    async def _upsert_products(self, payloads: list[NormalizedProduct], source: PimSource) -> ImportResult:
        summary = ImportResult()
        categories = await self.product_repository.get_categories_by_slugs(
            [slugify(item.category) for item in payloads if item.category]
        )
        existing_products = await self.product_repository.get_by_external_ids(
            [item.external_id for item in payloads if item.external_id]
        )
        existing_variants = await self.product_repository.get_by_skus(
            [variant.sku for item in payloads for variant in item.variants]
        )
        now = datetime.now(UTC)
        uploads_root = self.settings.uploads_root / "products"
        uploads_root.mkdir(parents=True, exist_ok=True)

        for item in payloads:
            summary.processed += 1
            product = None
            if item.external_id:
                product = existing_products.get(item.external_id)
            if product is None and item.variants:
                first_variant = existing_variants.get(item.variants[0].sku)
                if first_variant is not None:
                    product = await self.product_repository.get_product_by_id(first_variant.product_id)

            category = None
            if item.category:
                slug = slugify(item.category)
                category = categories.get(slug)
                if category is None:
                    category = Category(name=item.category, slug=slug)
                    await self.product_repository.add_category(category)
                    categories[slug] = category

            brand = await self._resolve_brand(item.brand)
            product_hash = self._hash_payload(item)
            if product is None:
                product = Product(
                    external_id=item.external_id or f"{source.name}-{uuid.uuid4()}",
                    source_hash=product_hash,
                    name=item.name,
                    slug=await self._ensure_unique_slug(item.name),
                    description=item.description,
                    brand=brand.name if brand else item.brand,
                    brand_id=brand.id if brand else None,
                    category_id=category.id if category else None,
                    status=ProductStatus.active,
                    is_active=True,
                    last_seen_at=now,
                )
                await self.product_repository.add_product(product)
                summary.created += 1
                summary.sync.products_created += 1
            else:
                changed = False
                for field_name, value in {
                    "name": item.name,
                    "description": item.description,
                    "brand": brand.name if brand else item.brand,
                    "brand_id": brand.id if brand else None,
                    "category_id": category.id if category else None,
                    "status": ProductStatus.active,
                    "is_active": True,
                    "last_seen_at": now,
                    "deleted_at": None,
                    "source_hash": product_hash,
                }.items():
                    if getattr(product, field_name) != value:
                        setattr(product, field_name, value)
                        changed = True
                if changed:
                    await self.product_repository.update_product(product)
                    summary.updated += 1
                    summary.sync.products_updated += 1
                else:
                    summary.sync.products_unchanged += 1

            await self._replace_attributes(product, item.attributes)

            for variant_payload in item.variants:
                variant = existing_variants.get(variant_payload.sku)
                variant_hash = self._hash_payload(
                    {
                        "sku": variant_payload.sku,
                        "ean": variant_payload.ean,
                        "size": variant_payload.size,
                        "color": variant_payload.color,
                        "price": variant_payload.price,
                        "stock_quantity": variant_payload.stock_quantity,
                        "is_active": variant_payload.is_active,
                    }
                )
                if variant is None:
                    variant = ProductVariant(
                        product_id=product.id,
                        sku=variant_payload.sku,
                        source_hash=variant_hash,
                        ean=variant_payload.ean,
                        color=variant_payload.color,
                        size=variant_payload.size,
                        price=variant_payload.price,
                        currency="SEK" if variant_payload.price is not None else None,
                        stock_quantity=variant_payload.stock_quantity,
                        is_active=variant_payload.is_active,
                        last_seen_at=now,
                    )
                    await self.product_repository.add_variant(variant)
                    existing_variants[variant.sku] = variant
                    summary.created += 1
                    summary.sync.variants_created += 1
                else:
                    changed = False
                    for field_name, value in {
                        "product_id": product.id,
                        "ean": variant_payload.ean,
                        "color": variant_payload.color,
                        "size": variant_payload.size,
                        "price": variant_payload.price,
                        "currency": "SEK" if variant_payload.price is not None else None,
                        "stock_quantity": variant_payload.stock_quantity,
                        "is_active": variant_payload.is_active,
                        "last_seen_at": now,
                        "deleted_at": None,
                        "source_hash": variant_hash,
                    }.items():
                        if getattr(variant, field_name) != value:
                            setattr(variant, field_name, value)
                            changed = True
                    if changed:
                        self.session.add(variant)
                        summary.updated += 1
                        summary.sync.variants_updated += 1
                    else:
                        summary.sync.variants_unchanged += 1

            for position, image_ref in enumerate(item.images):
                stored_image = await self._download_image(image_ref, uploads_root, source)
                existing = await self._find_image(product.id, stored_image["external_path"])
                if existing is None:
                    await self.product_repository.add_image(
                        ProductImage(
                            product_id=product.id,
                            variant_id=None,
                            external_path=stored_image["external_path"],
                            url=stored_image["url"],
                            local_path=stored_image["local_path"],
                            is_primary=position == 0,
                            sort_order=position,
                            position=position,
                        )
                    )
                    summary.sync.images_discovered += 1

        return summary

    def _parse(self, file_path: Path) -> list[NormalizedProduct]:
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            return CsvPimParser().parse(file_path)
        if suffix == ".json":
            return JsonPimParser().parse(file_path)
        if suffix == ".xml":
            return XmlPimParser().parse(file_path)
        raise ValueError(f"Unsupported import format: {suffix}")

    async def _resolve_brand(self, name: str | None) -> Brand | None:
        if not name:
            return None
        slug = slugify(name)
        brand = await self.product_repository.get_brand_by_slug(slug)
        if brand is None:
            brand = Brand(name=name, slug=slug)
            await self.product_repository.add_brand(brand)
        return brand

    async def _replace_attributes(self, product: Product, attributes: dict[str, str]) -> None:
        await self.product_repository.delete_product_attribute_values(product.id)
        for key, value in attributes.items():
            attribute = await self.product_repository.get_attribute_by_name(key)
            if attribute is None:
                attribute = Attribute(name=key, type=AttributeType.text)
                await self.product_repository.add_attribute(attribute)
            await self.product_repository.add_attribute_value(
                ProductAttributeValue(product_id=product.id, attribute_id=attribute.id, value=value)
            )

    async def _find_image(self, product_id: uuid.UUID, external_path: str) -> ProductImage | None:
        images = await self.product_repository.get_images_by_external_paths([external_path])
        return images.get(external_path)

    async def _download_image(self, image_ref: str, uploads_root: Path, source: PimSource) -> dict[str, str]:
        parsed = urlparse(image_ref)
        if parsed.scheme in {"http", "https"}:
            file_name = Path(parsed.path).name or f"{uuid.uuid4().hex}.img"
            target = uploads_root / f"{uuid.uuid4().hex}-{file_name}"
            with urlopen(image_ref) as response:
                target.write_bytes(response.read())
            return {
                "external_path": image_ref,
                "local_path": str(target),
                "url": f"/uploads/products/{target.name}",
            }

        if source.type in {PimSourceType.ftp, PimSourceType.sftp} and source.host:
            image_source = PimSource(
                id=source.id,
                name=source.name,
                type=source.type,
                host=source.host,
                port=source.port,
                username=source.username,
                password=source.password,
                path=image_ref,
                file_pattern=source.file_pattern,
                schedule=source.schedule,
                is_active=source.is_active,
            )
            downloaded = await self.downloader.download(image_source)
            target = uploads_root / downloaded.name
            if downloaded != target:
                shutil.copyfile(downloaded, target)
            return {
                "external_path": image_ref,
                "local_path": str(target),
                "url": f"/uploads/products/{target.name}",
            }

        local_path = Path(image_ref)
        if local_path.exists():
            target = uploads_root / f"{uuid.uuid4().hex}-{local_path.name}"
            shutil.copyfile(local_path, target)
            return {
                "external_path": image_ref,
                "local_path": str(target),
                "url": f"/uploads/products/{target.name}",
            }

        return {
            "external_path": image_ref,
            "local_path": image_ref,
            "url": image_ref,
        }

    async def _ensure_unique_slug(self, source: str) -> str:
        base_slug = slugify(source)
        slug = base_slug
        counter = 2
        while True:
            existing = await self.product_repository.get_any_product_by_slug(slug)
            if existing is None:
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    def _hash_payload(self, payload: object) -> str:
        normalized = repr(payload)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _advisory_lock_key(self, source_id: int) -> int:
        digest = hashlib.sha256(f"{self.settings.project_slug}:{source_id}".encode("utf-8")).digest()
        key = int.from_bytes(digest[:8], byteorder="big", signed=False)
        if key >= 2**63:
            key -= 2**64
        return key
