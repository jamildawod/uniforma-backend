import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.logging import get_logger
from app.core.text import slugify
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.repositories.product_repository import ProductRepository
from app.schemas.sync import PimSyncResponse


@dataclass(slots=True)
class VariantPayload:
    sku: str
    ean: str | None
    color: str | None
    size: str | None
    price: Decimal | None
    currency: str | None
    stock_quantity: int
    is_active: bool
    image_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProductPayload:
    external_id: str
    name: str
    slug: str
    description: str | None
    brand: str | None
    category_name: str | None
    is_active: bool
    variants: list[VariantPayload] = field(default_factory=list)


class PimIngestionService:
    def __init__(
        self,
        session: AsyncSession,
        product_repository: ProductRepository,
        settings: Settings,
    ) -> None:
        self.session = session
        self.product_repository = product_repository
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)

    async def ingest(self) -> PimSyncResponse:
        csv_path = self.settings.pim_csv_path
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        grouped = self._read_and_group(csv_path)
        response = PimSyncResponse()
        external_ids = list(grouped.keys())
        run_seen_at = datetime.now(UTC)

        try:
            for start in range(0, len(external_ids), self.settings.pim_batch_size):
                batch_ids = external_ids[start : start + self.settings.pim_batch_size]
                batch_payloads = [grouped[external_id] for external_id in batch_ids]
                batch_result = await self._process_batch(batch_payloads, run_seen_at)
                response.products_created += batch_result.products_created
                response.products_updated += batch_result.products_updated
                response.products_unchanged += batch_result.products_unchanged
                response.variants_created += batch_result.variants_created
                response.variants_updated += batch_result.variants_updated
                response.variants_unchanged += batch_result.variants_unchanged
                response.images_discovered += batch_result.images_discovered
                await self.session.commit()

            deleted_at = datetime.now(UTC)
            await self.product_repository.soft_delete_missing_variants(run_seen_at, deleted_at)
            await self.product_repository.soft_delete_missing_products(run_seen_at, deleted_at)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.error(
                "PIM ingestion integrity error",
                extra={
                    "event": "pim_ingestion_integrity_error",
                    "error": str(exc),
                },
            )
            raise

        self.logger.info(
            "PIM sync completed: products created=%s updated=%s unchanged=%s variants created=%s updated=%s unchanged=%s images discovered=%s",
            response.products_created,
            response.products_updated,
            response.products_unchanged,
            response.variants_created,
            response.variants_updated,
            response.variants_unchanged,
            response.images_discovered,
        )
        return response

    def _read_and_group(self, csv_path: Path) -> dict[str, ProductPayload]:
        grouped: dict[str, ProductPayload] = {}
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=self.settings.pim_csv_delimiter)
            headers = reader.fieldnames or []
            resolver = self._build_resolver(headers)

            for required in ("external_id", "name", "sku"):
                if required not in resolver:
                    raise ValueError(f"Missing required CSV column for {required}")

            for row in reader:
                external_id = self._get_value(row, resolver, "external_id")
                if not external_id:
                    continue

                product = grouped.get(external_id)
                if product is None:
                    name = self._get_value(row, resolver, "name") or external_id
                    category_name = self._get_value(row, resolver, "category")
                    product = ProductPayload(
                        external_id=external_id,
                        name=name,
                        slug=slugify(f"{name}-{external_id}"),
                        description=self._get_value(row, resolver, "description"),
                        brand=self._get_value(row, resolver, "brand"),
                        category_name=category_name,
                        is_active=self._get_bool(row, resolver, "product_is_active", default=True),
                    )
                    grouped[external_id] = product

                image_paths = self._get_image_paths(row, resolver)
                sku = self._get_value(row, resolver, "sku")
                if not sku:
                    continue

                product.variants.append(
                    VariantPayload(
                        sku=sku,
                        ean=self._get_value(row, resolver, "ean"),
                        color=self._get_value(row, resolver, "color"),
                        size=self._get_value(row, resolver, "size"),
                        price=self._get_decimal(row, resolver, "price"),
                        currency=self._get_value(row, resolver, "currency"),
                        stock_quantity=self._get_int(row, resolver, "stock_quantity"),
                        is_active=self._get_bool(row, resolver, "variant_is_active", default=True),
                        image_paths=image_paths,
                    )
                )
        return grouped

    def _build_resolver(self, headers: list[str]) -> dict[str, str]:
        normalized = {self._normalize_header(header): header for header in headers}
        aliases = {
            "external_id": ["external_id", "product_id", "style_no", "style", "artikelid", "artikelnummer"],
            "name": ["name", "product_name", "namn"],
            "description": ["description", "produktbeskrivning", "beskrivning"],
            "brand": ["brand", "varumarke", "varumärke"],
            "category": ["category", "kategori", "category_name"],
            "product_is_active": ["is_active", "active", "aktiv"],
            "sku": ["sku", "variant_sku", "artikelnummer_variant", "variantnummer"],
            "ean": ["ean", "gtin", "streckkod"],
            "color": ["color", "colour", "farg", "färg"],
            "size": ["size", "storlek"],
            "price": ["price", "pris"],
            "currency": ["currency", "valuta"],
            "stock_quantity": ["stock_quantity", "lager", "stock", "inventory"],
            "variant_is_active": ["variant_active", "variant_is_active", "variant_aktiv"],
            "image_paths": ["image_paths", "images", "image", "bild", "bildvag", "ftp_path", "ftp_paths"],
        }

        resolver: dict[str, str] = {}
        for canonical, candidates in aliases.items():
            for candidate in candidates:
                header = normalized.get(self._normalize_header(candidate))
                if header is not None:
                    resolver[canonical] = header
                    break
        return resolver

    def _compute_hash(self, data: dict[str, Any]) -> str:
        normalized = json.dumps(
            self._normalize_for_hash(data),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(normalized.encode()).hexdigest()

    def _normalize_for_hash(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return format(value, "f")
        if isinstance(value, dict):
            return {key: self._normalize_for_hash(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._normalize_for_hash(item) for item in value]
        if value is None:
            return None
        return value

    async def _process_batch(
        self,
        payloads: list[ProductPayload],
        run_seen_at: datetime,
    ) -> PimSyncResponse:
        result = PimSyncResponse()
        existing_products = await self.product_repository.get_by_external_ids(
            [payload.external_id for payload in payloads]
        )
        existing_variants = await self.product_repository.get_by_skus(
            [variant.sku for payload in payloads for variant in payload.variants]
        )
        category_names = [payload.category_name for payload in payloads if payload.category_name]
        category_slugs = [slugify(name) for name in category_names]
        categories = await self.product_repository.get_categories_by_slugs(category_slugs)
        existing_images = await self.product_repository.get_images_by_external_paths(
            [
                image_path
                for payload in payloads
                for variant in payload.variants
                for image_path in variant.image_paths
            ]
        )

        for payload in payloads:
            product = existing_products.get(payload.external_id)
            product_hash = self._compute_hash(
                {
                    "name": payload.name,
                    "slug": payload.slug,
                    "description": payload.description,
                    "brand": payload.brand,
                    "category": payload.category_name,
                    "is_active": payload.is_active,
                }
            )

            category = None
            if product is None or product.source_hash != product_hash:
                if payload.category_name:
                    category_slug = slugify(payload.category_name)
                    category = await self._resolve_category(categories, category_slug, payload.category_name)

            if product is None:
                product = Product(
                    external_id=payload.external_id,
                    source_hash=product_hash,
                    name=payload.name,
                    slug=payload.slug,
                    description=payload.description,
                    brand=payload.brand,
                    category_id=category.id if category else None,
                    is_active=payload.is_active,
                    last_seen_at=run_seen_at,
                    deleted_at=None,
                )
                await self.product_repository.add_product(product)
                await self.session.flush()
                existing_products[payload.external_id] = product
                result.products_created += 1
            elif product.source_hash == product_hash:
                product.last_seen_at = run_seen_at
                product.deleted_at = None
                result.products_unchanged += 1
            else:
                changed = self._update_if_changed(
                    product,
                    {
                        "name": payload.name,
                        "slug": payload.slug,
                        "description": payload.description,
                        "brand": payload.brand,
                        "category_id": category.id if category else None,
                        "is_active": payload.is_active,
                        "last_seen_at": run_seen_at,
                        "deleted_at": None,
                        "source_hash": product_hash,
                    },
                )
                if changed:
                    result.products_updated += 1
                else:
                    result.products_unchanged += 1

            for index, variant_payload in enumerate(payload.variants):
                variant_hash = self._compute_hash(
                    {
                        "ean": variant_payload.ean,
                        "color": variant_payload.color,
                        "size": variant_payload.size,
                        "price": variant_payload.price,
                        "currency": variant_payload.currency,
                        "stock_quantity": variant_payload.stock_quantity,
                        "is_active": variant_payload.is_active,
                    }
                )
                variant = existing_variants.get(variant_payload.sku)

                if variant is None:
                    variant = ProductVariant(
                        product_id=product.id,
                        sku=variant_payload.sku,
                        source_hash=variant_hash,
                        ean=variant_payload.ean,
                        color=variant_payload.color,
                        size=variant_payload.size,
                        price=variant_payload.price,
                        currency=variant_payload.currency,
                        stock_quantity=variant_payload.stock_quantity,
                        is_active=variant_payload.is_active,
                        last_seen_at=run_seen_at,
                        deleted_at=None,
                    )
                    await self.product_repository.add_variant(variant)
                    await self.session.flush()
                    existing_variants[variant_payload.sku] = variant
                    result.variants_created += 1
                elif variant.source_hash == variant_hash:
                    variant.last_seen_at = run_seen_at
                    variant.deleted_at = None
                    result.variants_unchanged += 1
                else:
                    changed = self._update_if_changed(
                        variant,
                        {
                            "product_id": product.id,
                            "ean": variant_payload.ean,
                            "color": variant_payload.color,
                            "size": variant_payload.size,
                            "price": variant_payload.price,
                            "currency": variant_payload.currency,
                            "stock_quantity": variant_payload.stock_quantity,
                            "is_active": variant_payload.is_active,
                            "last_seen_at": run_seen_at,
                            "deleted_at": None,
                            "source_hash": variant_hash,
                        },
                    )
                    if changed:
                        result.variants_updated += 1
                    else:
                        result.variants_unchanged += 1

                for image_index, image_path in enumerate(variant_payload.image_paths):
                    if image_path in existing_images:
                        continue
                    image = ProductImage(
                        product_id=product.id,
                        variant_id=variant.id,
                        external_path=image_path,
                        local_path=None,
                        is_primary=image_index == 0 and index == 0,
                        sort_order=image_index,
                    )
                    await self.product_repository.add_image(image)
                    existing_images[image_path] = image
                    result.images_discovered += 1

        return result

    async def _resolve_category(
        self,
        categories: dict[str, Category],
        category_slug: str,
        category_name: str,
    ) -> Category:
        category = categories.get(category_slug)
        if category is None:
            category = Category(name=category_name, slug=category_slug)
            await self.product_repository.add_category(category)
            await self.session.flush()
            categories[category_slug] = category
        return category

    def _update_if_changed(self, model: object, values: dict[str, object]) -> bool:
        changed = False
        for field_name, value in values.items():
            if getattr(model, field_name) != value:
                setattr(model, field_name, value)
                changed = True
        return changed

    def _normalize_header(self, value: str) -> str:
        return "".join(char for char in value.lower() if char.isalnum() or char == "_")

    def _get_value(self, row: dict[str, str], resolver: dict[str, str], field: str) -> str | None:
        header = resolver.get(field)
        if header is None:
            return None
        value = row.get(header)
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    def _get_int(self, row: dict[str, str], resolver: dict[str, str], field: str) -> int:
        value = self._get_value(row, resolver, field)
        if value is None:
            return 0
        try:
            return int(value)
        except ValueError:
            return 0

    def _get_decimal(self, row: dict[str, str], resolver: dict[str, str], field: str) -> Decimal | None:
        value = self._get_value(row, resolver, field)
        if value is None:
            return None
        try:
            return Decimal(value.replace(",", "."))
        except InvalidOperation:
            return None

    def _get_bool(
        self,
        row: dict[str, str],
        resolver: dict[str, str],
        field: str,
        default: bool,
    ) -> bool:
        value = self._get_value(row, resolver, field)
        if value is None:
            return default
        return value.lower() in {"1", "true", "yes", "ja", "y"}

    def _get_image_paths(self, row: dict[str, str], resolver: dict[str, str]) -> list[str]:
        value = self._get_value(row, resolver, "image_paths")
        if value is None:
            return []
        return [item.strip() for item in value.replace("|", ",").split(",") if item.strip()]
