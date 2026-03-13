from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pim_import_run import PimImportRun
from app.models.pim_source import PimSource


class PimRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_sources(self, active_only: bool = False) -> list[PimSource]:
        statement = select(PimSource).order_by(PimSource.name.asc())
        if active_only:
            statement = statement.where(PimSource.is_active.is_(True))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_source(self, source_id: int) -> PimSource | None:
        result = await self.session.execute(select(PimSource).where(PimSource.id == source_id))
        return result.scalar_one_or_none()

    async def add_source(self, source: PimSource) -> PimSource:
        self.session.add(source)
        await self.session.flush()
        return source

    async def list_import_runs(self, limit: int = 50) -> list[PimImportRun]:
        result = await self.session.execute(
            select(PimImportRun)
            .options(selectinload(PimImportRun.source))
            .order_by(PimImportRun.started_at.desc(), PimImportRun.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_import_run(self, run: PimImportRun) -> PimImportRun:
        self.session.add(run)
        await self.session.flush()
        return run
