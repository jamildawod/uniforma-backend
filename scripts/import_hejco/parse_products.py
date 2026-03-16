from __future__ import annotations

import json
from dataclasses import asdict

from app.core.config import get_settings
from app.services.hejco_import_service import HejcoImportService


def parse_products() -> list[dict]:
    settings = get_settings()
    service = HejcoImportService(None, settings, None)
    return [asdict(product) for product in service.parse_products()]


if __name__ == "__main__":
    print(json.dumps(parse_products(), indent=2, ensure_ascii=True, default=str))
