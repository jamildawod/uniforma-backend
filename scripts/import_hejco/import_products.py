from __future__ import annotations

import asyncio
import json

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.repositories.product_repository import ProductRepository
from app.services.hejco_import_service import HejcoImportService


async def main() -> None:
    summary = await import_products()
    print(json.dumps(summary, indent=2, ensure_ascii=True))


async def import_products() -> dict[str, int]:
    settings = get_settings()
    async with get_session_factory()() as session:
        service = HejcoImportService(session, settings, ProductRepository(session))
        summary = await service.import_products()
        return summary.__dict__


if __name__ == "__main__":
    asyncio.run(main())
