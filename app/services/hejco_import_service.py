from __future__ import annotations

import asyncio
import csv
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from ftplib import FTP, error_perm
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.text import slugify
from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product, ProductStatus
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.repositories.product_repository import ProductRepository
from app.services.cache_service import CacheService
from app.services.image_optimization_service import optimize_images


HEJCO_CATEGORY_MAP = {
    "dental": "Dental",
    "tand": "Dental",
    "djur": "Djursjukvård",
    "veterinar": "Djursjukvård",
    "vard": "Vård & Omsorg",
    "omsorg": "Vård & Omsorg",
    "stad": "Städ & Service",
    "service": "Städ & Service",
    "kok": "Kök",
    "kitchen": "Kök",
    "skonhet": "Skönhet & Hälsa",
    "halsa": "Skönhet & Hälsa",
    "beauty": "Skönhet & Hälsa",
    "health": "Skönhet & Hälsa",
}


@dataclass(slots=True)
class HejcoProductRecord:
    sku: str
    name: str
    description: str | None
    category: str | None
    subcategory: str | None
    color: str | None
    size: str | None
    price: Decimal | None
    brand: str | None
    style_id: str
    raw: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class HejcoImportSummary:
    products_imported: int = 0
    products_updated: int = 0
    images_matched: int = 0
    stock_updated: int = 0
    variants_imported: int = 0
    variants_updated: int = 0


class HejcoImageMatcher:
    def __init__(self, images_root: Path) -> None:
        self.images_root = images_root

    @lru_cache(maxsize=8192)
    def find_product_images(self, sku: str) -> tuple[str, ...]:
        if not self.images_root.exists():
            return ()
        prefix = str(sku).strip()
        matches = sorted(
            path.name
            for path in self.images_root.iterdir()
            if path.is_file() and path.name.startswith(prefix)
        )
        return tuple(matches)

    def clear(self) -> None:
        self.find_product_images.cache_clear()


class HejcoImportService:
    def __init__(
        self,
        session: AsyncSession | None,
        settings: Settings,
        product_repository: ProductRepository | None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.product_repository = product_repository
        self.image_matcher = HejcoImageMatcher(settings.hejco_images_root)

    def ensure_data_directories(self) -> None:
        for path in (
            self.settings.hejco_data_root,
            self.settings.hejco_images_root,
            self.settings.hejco_csv_root,
            self.settings.hejco_work_root,
            self.settings.hejco_stock_root,
        ):
            path.mkdir(parents=True, exist_ok=True)

    async def download_from_ftp(self) -> dict[str, int]:
        self.ensure_data_directories()
        return await asyncio.to_thread(self._download_from_ftp)

    def _download_from_ftp(self) -> dict[str, int]:
        if not self.settings.hejco_ftp_user or not self.settings.hejco_ftp_pass:
            raise ValueError("HEJCO_FTP_USER and HEJCO_FTP_PASS must be configured.")

        ftp = FTP()
        ftp.connect(
            host=self.settings.hejco_ftp_host,
            port=21,
            timeout=self.settings.hejco_ftp_timeout_seconds,
        )
        ftp.login(self.settings.hejco_ftp_user, self.settings.hejco_ftp_pass)
        counters = {"images": 0, "csv": 0, "stock": 0}
        downloaded_images: list[Path] = []
        try:
            counters["images"] = self._download_tree(
                ftp,
                PurePosixPath("/Hejco/Pictures/jpeg"),
                self.settings.hejco_images_root,
                downloaded_files=downloaded_images,
            )
            counters["csv"] = self._download_tree(
                ftp,
                PurePosixPath("/Hejco/product_data/Swedish"),
                self.settings.hejco_csv_root,
                file_names={"PIMexport_Hejco_sv-SE.csv"},
            )
            counters["stock"] = self._download_tree(
                ftp,
                PurePosixPath("/Hejco/stock_availability"),
                self.settings.hejco_stock_root,
            )
        finally:
            ftp.quit()
        optimize_images(self.settings.hejco_images_root, self.settings.hejco_images_root, downloaded_images)
        self.image_matcher.clear()
        return counters

    def _download_tree(
        self,
        ftp: FTP,
        remote_dir: PurePosixPath,
        local_dir: Path,
        file_names: set[str] | None = None,
        downloaded_files: list[Path] | None = None,
    ) -> int:
        local_dir.mkdir(parents=True, exist_ok=True)
        downloaded = 0
        for entry in self._list_remote_entries(ftp, remote_dir):
            remote_path = remote_dir / entry["name"]
            if entry["type"] == "dir":
                downloaded += self._download_tree(
                    ftp,
                    remote_path,
                    local_dir / entry["name"],
                    file_names=file_names,
                    downloaded_files=downloaded_files,
                )
                continue
            if file_names and entry["name"] not in file_names:
                continue
            target = local_dir / entry["name"]
            with target.open("wb") as handle:
                ftp.retrbinary(f"RETR {remote_path.as_posix()}", handle.write)
            if downloaded_files is not None:
                downloaded_files.append(target.resolve())
            downloaded += 1
        return downloaded

    def _list_remote_entries(self, ftp: FTP, remote_dir: PurePosixPath) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        try:
            for name, facts in ftp.mlsd(remote_dir.as_posix()):
                if name in {".", ".."}:
                    continue
                entries.append({"name": name, "type": facts.get("type", "file")})
            return entries
        except (error_perm, AttributeError):
            names = ftp.nlst(remote_dir.as_posix())
            base = remote_dir.as_posix().rstrip("/")
            for item in names:
                name = item.rsplit("/", 1)[-1]
                if not name or name in {".", ".."}:
                    continue
                entry_type = "dir" if self._is_remote_directory(ftp, item) else "file"
                entries.append({"name": name, "type": entry_type})
            return entries

    def _is_remote_directory(self, ftp: FTP, remote_path: str) -> bool:
        current = ftp.pwd()
        try:
            ftp.cwd(remote_path)
            return True
        except error_perm:
            return False
        finally:
            ftp.cwd(current)

    def parse_products(self, csv_path: Path | None = None) -> list[HejcoProductRecord]:
        self.ensure_data_directories()
        source = csv_path or self.settings.hejco_csv_file
        if not source.exists():
            raise FileNotFoundError(f"Hejco CSV not found: {source}")

        records: list[HejcoProductRecord] = []
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            resolver = self._build_resolver(reader.fieldnames or [])
            for row in reader:
                sku = self._clean(self._get_value(row, resolver, "sku"))
                if not sku:
                    continue
                name = self._clean(self._get_value(row, resolver, "name")) or sku
                category = self.normalize_category(self._clean(self._get_value(row, resolver, "category")))
                subcategory = self._clean(self._get_value(row, resolver, "subcategory"))
                brand = self._clean(self._get_value(row, resolver, "brand")) or "Hejco"
                style_id = (
                    self._clean(self._get_value(row, resolver, "style_id"))
                    or self._sku_prefix(sku)
                    or sku
                )
                records.append(
                    HejcoProductRecord(
                        sku=sku,
                        name=name,
                        description=self._clean(self._get_value(row, resolver, "description")),
                        category=category,
                        subcategory=subcategory,
                        color=self._clean(self._get_value(row, resolver, "color")),
                        size=self._clean(self._get_value(row, resolver, "size")),
                        price=self._parse_decimal(self._get_value(row, resolver, "price")),
                        brand=brand,
                        style_id=style_id,
                        raw={key: self._clean(value) or "" for key, value in row.items() if key},
                    )
                )
        return records

    async def import_products(self, records: list[HejcoProductRecord] | None = None) -> HejcoImportSummary:
        session = self._require_session()
        repository = self._require_product_repository()
        parsed_records = records or self.parse_products()
        grouped = self._group_records(parsed_records)
        summary = HejcoImportSummary()
        existing_products = await repository.get_by_external_ids(list(grouped.keys()))
        existing_variants = await repository.get_by_skus(
            [record.sku for rows in grouped.values() for record in rows]
        )
        category_names = {
            record.category
            for rows in grouped.values()
            for record in rows
            if record.category
        }
        subcategory_names = {
            (record.category, record.subcategory)
            for rows in grouped.values()
            for record in rows
            if record.category and record.subcategory
        }
        categories = await repository.get_categories_by_slugs([slugify(name) for name in category_names])
        brands = await self._get_existing_brands({record.brand for rows in grouped.values() for record in rows if record.brand})
        existing_images = await repository.get_images_by_external_paths(
            [
                f"/images/products/{filename}"
                for style_id in grouped
                for filename in self.find_product_images(style_id)
            ]
        )
        run_seen_at = datetime.now(UTC)
        advisory_lock_key = self._advisory_lock_key()
        lock_result = await session.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": advisory_lock_key})
        if not bool(lock_result.scalar()):
            raise RuntimeError("Hejco import already running.")

        try:
            child_categories: dict[tuple[str, str], Category] = {}
            for category_name, subcategory_name in subcategory_names:
                child = await self._get_or_create_subcategory(
                    categories,
                    child_categories,
                    category_name,
                    subcategory_name,
                )
                child_categories[(category_name, subcategory_name)] = child

            for index, (external_id, rows) in enumerate(grouped.items(), start=1):
                primary = rows[0]
                product = existing_products.get(external_id)
                brand = await self._get_or_create_brand(brands, primary.brand)
                category = None
                if primary.subcategory and primary.category:
                    category = child_categories[(primary.category, primary.subcategory)]
                elif primary.category:
                    category = await self._get_or_create_category(categories, primary.category)

                image_names = self.find_product_images(external_id)
                product_hash = self._hash_payload(
                    {
                        "external_id": external_id,
                        "name": primary.name,
                        "description": primary.description,
                        "brand": primary.brand,
                        "category": primary.category,
                        "subcategory": primary.subcategory,
                        "images": image_names,
                    }
                )

                if product is None:
                    product = Product(
                        external_id=external_id,
                        source_hash=product_hash,
                        name=primary.name,
                        slug=await self._ensure_unique_slug(f"{primary.name}-{external_id}"),
                        description=primary.description,
                        brand=brand.name if brand else primary.brand,
                        brand_id=brand.id if brand else None,
                        category_id=category.id if category else None,
                        status=ProductStatus.active,
                        is_active=True,
                        last_seen_at=run_seen_at,
                    )
                    session.add(product)
                    await session.flush()
                    existing_products[external_id] = product
                    summary.products_imported += 1
                else:
                    changed = self._update_if_changed(
                        product,
                        {
                            "source_hash": product_hash,
                            "name": primary.name,
                            "description": primary.description,
                            "brand": brand.name if brand else primary.brand,
                            "brand_id": brand.id if brand else None,
                            "category_id": category.id if category else None,
                            "status": ProductStatus.active,
                            "is_active": True,
                            "last_seen_at": run_seen_at,
                            "deleted_at": None,
                        },
                    )
                    if changed:
                        session.add(product)
                        summary.products_updated += 1

                for row in rows:
                    variant = existing_variants.get(row.sku)
                    variant_hash = self._hash_payload(
                        {
                            "product_id": str(product.id),
                            "sku": row.sku,
                            "color": row.color,
                            "size": row.size,
                            "price": row.price,
                        }
                    )
                    if variant is None:
                        variant = ProductVariant(
                            product_id=product.id,
                            sku=row.sku,
                            source_hash=variant_hash,
                            color=row.color,
                            size=row.size,
                            price=row.price,
                            currency="SEK" if row.price is not None else None,
                            stock_quantity=0,
                            is_active=True,
                            last_seen_at=run_seen_at,
                        )
                        session.add(variant)
                        existing_variants[row.sku] = variant
                        summary.variants_imported += 1
                    else:
                        changed = self._update_if_changed(
                            variant,
                            {
                                "product_id": product.id,
                                "source_hash": variant_hash,
                                "color": row.color,
                                "size": row.size,
                                "price": row.price,
                                "currency": "SEK" if row.price is not None else None,
                                "is_active": True,
                                "last_seen_at": run_seen_at,
                                "deleted_at": None,
                            },
                        )
                        if changed:
                            session.add(variant)
                            summary.variants_updated += 1

                for position, image_name in enumerate(image_names):
                    image_url = f"/images/products/{image_name}"
                    if image_url in existing_images:
                        continue
                    image = ProductImage(
                        product_id=product.id,
                        external_path=image_url,
                        url=image_url,
                        local_path=str(self.settings.hejco_images_root / image_name),
                        is_primary=position == 0,
                        sort_order=position,
                        position=position,
                    )
                    await session.merge(image)
                    existing_images[image_url] = image
                    summary.images_matched += 1

                if index % self.settings.hejco_batch_size == 0:
                    await session.commit()
                    await session.flush()

            await session.commit()
            return summary
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": advisory_lock_key})

    async def sync_stock(self) -> int:
        session = self._require_session()
        repository = self._require_product_repository()
        stock_rows = self.load_stock_rows()
        variants = await repository.get_by_skus(list(stock_rows.keys()))
        updated = 0
        for sku, quantity in stock_rows.items():
            variant = variants.get(sku)
            if variant is None or variant.stock_quantity == quantity:
                continue
            variant.stock_quantity = quantity
            session.add(variant)
            updated += 1
        if updated:
            await session.commit()
        return updated

    async def run_full_sync(self) -> HejcoImportSummary:
        await self.download_from_ftp()
        summary = await self.import_products()
        summary.stock_updated = await self.sync_stock()
        await self.refresh_product_list_view()
        return summary

    async def refresh_product_list_view(self) -> None:
        session = self._require_session()
        populated = await session.execute(
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
        has_unique_index = await session.execute(
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
            await session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY product_list_view"))
        else:
            await session.execute(text("REFRESH MATERIALIZED VIEW product_list_view"))
        await session.commit()
        await CacheService(self.settings).bump_version("catalog")

    def load_stock_rows(self) -> dict[str, int]:
        self.ensure_data_directories()
        stock_files = sorted(path for path in self.settings.hejco_stock_root.glob("*") if path.is_file())
        if not stock_files:
            return {}
        latest = stock_files[-1]
        with latest.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            delimiter = ";" if sample.count(";") >= sample.count(",") else ","
            reader = csv.DictReader(handle, delimiter=delimiter)
            resolver = self._build_stock_resolver(reader.fieldnames or [])
            stock_rows: dict[str, int] = {}
            for row in reader:
                sku = self._clean(self._get_value(row, resolver, "sku"))
                if not sku:
                    continue
                stock_rows[sku] = self._parse_int(self._get_value(row, resolver, "stock"))
            return stock_rows

    def find_product_images(self, sku: str) -> list[str]:
        return list(self.image_matcher.find_product_images(sku))

    async def _get_existing_brands(self, names: set[str]) -> dict[str, Brand]:
        session = self._require_session()
        brands: dict[str, Brand] = {}
        if not names:
            return brands
        result = await session.execute(select(Brand).where(Brand.slug.in_([slugify(name) for name in names])))
        for brand in result.scalars().all():
            brands[brand.slug] = brand
        return brands

    async def _get_or_create_brand(self, brands: dict[str, Brand], name: str | None) -> Brand | None:
        session = self._require_session()
        if not name:
            return None
        brand_slug = slugify(name)
        brand = brands.get(brand_slug)
        if brand is None:
            brand = Brand(name=name, slug=brand_slug)
            session.add(brand)
            await session.flush()
            brands[brand_slug] = brand
        return brand

    async def _get_or_create_category(self, categories: dict[str, Category], name: str) -> Category:
        session = self._require_session()
        category_slug = slugify(name)
        category = categories.get(category_slug)
        if category is None:
            category = Category(name=name, slug=category_slug)
            session.add(category)
            await session.flush()
            categories[category_slug] = category
        return category

    async def _get_or_create_subcategory(
        self,
        categories: dict[str, Category],
        child_categories: dict[tuple[str, str], Category],
        category_name: str,
        subcategory_name: str,
    ) -> Category:
        session = self._require_session()
        key = (category_name, subcategory_name)
        existing = child_categories.get(key)
        if existing is not None:
            return existing
        parent = await self._get_or_create_category(categories, category_name)
        slug = slugify(f"{category_name}-{subcategory_name}")
        result = await session.execute(select(Category).where(Category.slug == slug))
        child = result.scalar_one_or_none()
        if child is None:
            child = Category(name=subcategory_name, slug=slug, parent_id=parent.id)
            session.add(child)
            await session.flush()
        child_categories[key] = child
        return child

    async def _ensure_unique_slug(self, base: str) -> str:
        repository = self._require_product_repository()
        candidate = slugify(base)
        suffix = 1
        while await repository.get_any_product_by_slug(candidate) is not None:
            suffix += 1
            candidate = f"{slugify(base)}-{suffix}"
        return candidate

    def normalize_category(self, raw_value: str | None) -> str | None:
        if not raw_value:
            return None
        normalized = slugify(raw_value)
        for needle, mapped in HEJCO_CATEGORY_MAP.items():
            if needle in normalized:
                return mapped
        return raw_value.strip()

    def _group_records(self, records: list[HejcoProductRecord]) -> dict[str, list[HejcoProductRecord]]:
        grouped: dict[str, list[HejcoProductRecord]] = {}
        for record in records:
            grouped.setdefault(record.style_id, []).append(record)
        return grouped

    def _build_resolver(self, headers: list[str]) -> dict[str, str]:
        aliases = {
            "sku": ["sku", "artikelnummer", "article_no", "itemnumber", "style_no"],
            "style_id": ["style_id", "style", "modell", "modellnummer", "model_no"],
            "name": ["name", "namn", "product_name", "produktnamn"],
            "description": ["description", "beskrivning", "produktbeskrivning"],
            "category": ["category", "kategori", "segment", "main_category"],
            "subcategory": ["subcategory", "underkategori", "sub_category"],
            "color": ["color", "colour", "farg", "färg"],
            "size": ["size", "storlek"],
            "price": ["price", "pris", "recommended_price"],
            "brand": ["brand", "varumarke", "varumärke"],
        }
        normalized = {self._normalize_header(header): header for header in headers}
        resolver: dict[str, str] = {}
        for canonical, candidates in aliases.items():
            for candidate in candidates:
                resolved = normalized.get(self._normalize_header(candidate))
                if resolved is not None:
                    resolver[canonical] = resolved
                    break
        return resolver

    def _build_stock_resolver(self, headers: list[str]) -> dict[str, str]:
        aliases = {
            "sku": ["sku", "artikelnummer", "itemnumber", "style_no"],
            "stock": ["stock", "lager", "available", "availability", "quantity"],
        }
        normalized = {self._normalize_header(header): header for header in headers}
        resolver: dict[str, str] = {}
        for canonical, candidates in aliases.items():
            for candidate in candidates:
                resolved = normalized.get(self._normalize_header(candidate))
                if resolved is not None:
                    resolver[canonical] = resolved
                    break
        return resolver

    def _get_value(self, row: dict[str, Any], resolver: dict[str, str], key: str) -> str | None:
        header = resolver.get(key)
        if header is None:
            return None
        value = row.get(header)
        return str(value) if value is not None else None

    def _normalize_header(self, value: str) -> str:
        return slugify(value).replace("-", "_")

    def _parse_decimal(self, value: str | None) -> Decimal | None:
        cleaned = self._clean(value)
        if not cleaned:
            return None
        try:
            return Decimal(cleaned.replace(" ", "").replace(",", "."))
        except InvalidOperation:
            return None

    def _parse_int(self, value: str | None) -> int:
        cleaned = self._clean(value)
        if not cleaned:
            return 0
        try:
            return int(float(cleaned.replace(",", ".")))
        except ValueError:
            return 0

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = str(value).strip()
        return stripped or None

    def _sku_prefix(self, sku: str) -> str:
        digits = []
        for char in sku:
            if char.isdigit():
                digits.append(char)
                continue
            break
        return "".join(digits) or sku

    def _hash_payload(self, payload: dict[str, Any]) -> str:
        normalized = repr(sorted(payload.items())).encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()

    def _update_if_changed(self, instance: Any, values: dict[str, Any]) -> bool:
        changed = False
        for field_name, value in values.items():
            if getattr(instance, field_name) != value:
                setattr(instance, field_name, value)
                changed = True
        return changed

    def _advisory_lock_key(self) -> int:
        digest = hashlib.sha256(f"{self.settings.project_slug}:hejco".encode("utf-8")).digest()
        key = int.from_bytes(digest[:8], byteorder="big", signed=False)
        if key >= 2**63:
            key -= 2**64
        return key

    def _require_session(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError("Hejco import service requires a database session for this operation.")
        return self.session

    def _require_product_repository(self) -> ProductRepository:
        if self.product_repository is None:
            raise RuntimeError("Hejco import service requires a product repository for this operation.")
        return self.product_repository
