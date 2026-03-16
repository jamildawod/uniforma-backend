#!/usr/bin/env python3
"""PIM import scaffold for future CSV/API product ingestion."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PimProduct:
    name: str
    description: str | None = None
    brand: str | None = None
    variants: list[dict[str, Any]] = field(default_factory=list)
    images: list[str] = field(default_factory=list)


class PimImporter:
    """Thin importer interface for future PIM integrations."""

    def load_from_csv(self, file_path: Path) -> list[PimProduct]:
        products: list[PimProduct] = []
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                products.append(
                    PimProduct(
                        name=row.get("name", "").strip(),
                        description=(row.get("description") or "").strip() or None,
                        brand=(row.get("brand") or "").strip() or None,
                        variants=self._parse_variants(row.get("variants")),
                        images=self._parse_images(row.get("images")),
                    )
                )
        return products

    def load_from_api(self, payload: list[dict[str, Any]]) -> list[PimProduct]:
        return [
            PimProduct(
                name=item.get("name", "").strip(),
                description=(item.get("description") or "").strip() or None,
                brand=(item.get("brand") or "").strip() or None,
                variants=list(item.get("variants") or []),
                images=[str(image) for image in item.get("images") or []],
            )
            for item in payload
        ]

    def normalize(self, products: list[PimProduct]) -> list[dict[str, Any]]:
        return [
            {
                "name": product.name,
                "description": product.description,
                "brand": product.brand,
                "variants": product.variants,
                "images": product.images,
            }
            for product in products
        ]

    def _parse_variants(self, raw_value: str | None) -> list[dict[str, Any]]:
        if not raw_value:
            return []
        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            return []
        return decoded if isinstance(decoded, list) else []

    def _parse_images(self, raw_value: str | None) -> list[str]:
        if not raw_value:
            return []
        return [item.strip() for item in raw_value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare product payloads for future PIM imports.")
    parser.add_argument("--csv", type=Path, help="Source CSV exported from the PIM")
    args = parser.parse_args()

    importer = PimImporter()
    if args.csv:
        print(json.dumps(importer.normalize(importer.load_from_csv(args.csv)), indent=2, ensure_ascii=True))
        return
    parser.print_help()


if __name__ == "__main__":
    main()
