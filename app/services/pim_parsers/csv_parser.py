import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.core.text import slugify
from app.services.pim_parsers.common import NormalizedProduct, NormalizedVariant


class CsvPimParser:
    def parse(self, file_path: Path) -> list[NormalizedProduct]:
        grouped: dict[str, NormalizedProduct] = {}
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                sku = self._clean(row.get("sku")) or self._clean(row.get("variant_sku"))
                if not sku:
                    continue
                external_id = self._clean(row.get("external_id")) or sku
                key = external_id
                product = grouped.get(key)
                if product is None:
                    name = self._clean(row.get("name")) or sku
                    product = NormalizedProduct(
                        name=name,
                        description=self._clean(row.get("description")),
                        brand=self._clean(row.get("brand")),
                        category=self._clean(row.get("category")),
                        external_id=external_id,
                    )
                    grouped[key] = product

                images = self._split_list(row.get("images") or row.get("image") or row.get("image_url"))
                for image in images:
                    if image not in product.images:
                        product.images.append(image)

                reserved = {
                    "external_id",
                    "name",
                    "description",
                    "brand",
                    "category",
                    "sku",
                    "variant_sku",
                    "ean",
                    "size",
                    "color",
                    "price",
                    "stock_quantity",
                    "images",
                    "image",
                    "image_url",
                }
                for raw_key, raw_value in row.items():
                    if raw_key in reserved:
                        continue
                    value = self._clean(raw_value)
                    if value:
                        product.attributes[slugify(raw_key).replace("-", "_")] = value

                product.variants.append(
                    NormalizedVariant(
                        sku=sku,
                        ean=self._clean(row.get("ean")),
                        size=self._clean(row.get("size")),
                        color=self._clean(row.get("color")),
                        price=self._decimal(row.get("price")),
                        stock_quantity=self._int(row.get("stock_quantity")),
                        is_active=True,
                    )
                )

        return list(grouped.values())

    def _split_list(self, value: str | None) -> list[str]:
        if not value:
            return []
        return [item.strip() for item in value.replace("|", ",").split(",") if item.strip()]

    def _decimal(self, value: str | None) -> Decimal | None:
        cleaned = self._clean(value)
        if cleaned is None:
            return None
        try:
            return Decimal(cleaned.replace(",", "."))
        except InvalidOperation:
            return None

    def _int(self, value: str | None) -> int:
        cleaned = self._clean(value)
        if cleaned is None:
            return 0
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
