from __future__ import annotations

"""Nightly Hejco sync entrypoint.

Cron example:
0 3 * * * cd /opt/uniforma && python scripts/run_hejco_sync.py
"""

import asyncio
import json

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.repositories.product_repository import ProductRepository
from app.services.hejco_import_service import HejcoImportService


async def main() -> None:
    settings = get_settings()
    async with get_session_factory()() as session:
        service = HejcoImportService(session, settings, ProductRepository(session))
        summary = await service.run_full_sync()
        print(json.dumps(summary.__dict__, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
