from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import HealthResponse


class HealthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def status(self) -> HealthResponse:
        await self.session.execute(text("SELECT 1"))
        return HealthResponse(status="ok", database="up")
