from __future__ import annotations

import argparse
import json

from app.core.config import get_settings
from app.services.hejco_import_service import HejcoImportService


def find_product_images(sku: str) -> list[str]:
    settings = get_settings()
    service = HejcoImportService(None, settings, None)
    return service.find_product_images(sku)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find Hejco images by SKU prefix.")
    parser.add_argument("sku")
    args = parser.parse_args()
    print(json.dumps(find_product_images(args.sku), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
