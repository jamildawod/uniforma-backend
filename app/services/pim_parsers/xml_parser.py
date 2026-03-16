from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree

from app.services.pim_parsers.common import NormalizedProduct, NormalizedVariant


class XmlPimParser:
    def parse(self, file_path: Path) -> list[NormalizedProduct]:
        tree = ElementTree.parse(file_path)
        root = tree.getroot()
        products: list[NormalizedProduct] = []

        for product_node in root.findall(".//product"):
            variants = []
            for variant_node in product_node.findall("./variants/variant"):
                sku = (variant_node.findtext("sku") or "").strip()
                if not sku:
                    continue
                variants.append(
                    NormalizedVariant(
                        sku=sku,
                        ean=self._clean(variant_node.findtext("ean")),
                        size=self._clean(variant_node.findtext("size")),
                        color=self._clean(variant_node.findtext("color")),
                        price=self._decimal(variant_node.findtext("price")),
                        stock_quantity=self._int(variant_node.findtext("stock_quantity")),
                        is_active=(variant_node.findtext("is_active") or "true").strip().lower() in {"1", "true", "yes"},
                    )
                )

            images = [text.strip() for text in (node.text for node in product_node.findall("./images/image")) if text and text.strip()]
            attributes = {
                (node.get("name") or "").strip(): (node.text or "").strip()
                for node in product_node.findall("./attributes/attribute")
                if (node.get("name") or "").strip() and (node.text or "").strip()
            }
            name = (product_node.findtext("name") or "").strip()
            if not name:
                continue
            products.append(
                NormalizedProduct(
                    name=name,
                    description=self._clean(product_node.findtext("description")),
                    brand=self._clean(product_node.findtext("brand")),
                    category=self._clean(product_node.findtext("category")),
                    external_id=self._clean(product_node.findtext("external_id")),
                    variants=variants,
                    images=images,
                    attributes=attributes,
                )
            )

        return products

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    def _int(self, value: str | None) -> int:
        if not value:
            return 0
        try:
            return int(value)
        except ValueError:
            return 0

    def _decimal(self, value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            return None
