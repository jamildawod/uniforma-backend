from __future__ import annotations

import asyncio
import json

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.repositories.product_repository import ProductRepository
from app.services.hejco_import_service import HejcoImportService


async def main() -> None:
    result = await download_from_ftp()
    print(json.dumps(result, indent=2, ensure_ascii=True))


async def download_from_ftp() -> dict[str, int]:
    settings = get_settings()
    async with get_session_factory()() as session:
        service = HejcoImportService(session, settings, ProductRepository(session))
        return await service.download_from_ftp()


if __name__ == "__main__":
    asyncio.run(main())
