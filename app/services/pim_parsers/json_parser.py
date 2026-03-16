import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.services.pim_parsers.common import NormalizedProduct, NormalizedVariant


class JsonPimParser:
    def parse(self, file_path: Path) -> list[NormalizedProduct]:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else payload.get("products", [])
        products: list[NormalizedProduct] = []
        for item in items:
            variants = [
                NormalizedVariant(
                    sku=str(variant.get("sku", "")).strip(),
                    ean=self._maybe(variant.get("ean")),
                    size=self._maybe(variant.get("size")),
                    color=self._maybe(variant.get("color")),
                    price=self._decimal(variant.get("price")),
                    stock_quantity=int(variant.get("stock_quantity") or 0),
                    is_active=bool(variant.get("is_active", True)),
                )
                for variant in item.get("variants", [])
                if str(variant.get("sku", "")).strip()
            ]
            products.append(
                NormalizedProduct(
                    name=str(item.get("name") or "").strip(),
                    description=self._maybe(item.get("description")),
                    brand=self._maybe(item.get("brand")),
                    category=self._maybe(item.get("category")),
                    external_id=self._maybe(item.get("external_id")),
                    variants=variants,
                    images=[str(image).strip() for image in item.get("images", []) if str(image).strip()],
                    attributes={str(key): str(value) for key, value in (item.get("attributes") or {}).items() if value is not None},
                )
            )
        return [product for product in products if product.name]

    def _maybe(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _decimal(self, value: object) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None
