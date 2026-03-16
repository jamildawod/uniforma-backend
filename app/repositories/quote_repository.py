from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quote_request import QuoteRequest


class QuoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, quote_request: QuoteRequest) -> QuoteRequest:
        self.session.add(quote_request)
        await self.session.flush()
        return quote_request

    async def list_quotes(self, limit: int = 50, offset: int = 0) -> list[QuoteRequest]:
        statement = (
            select(QuoteRequest)
            .options(
                selectinload(QuoteRequest.product),
                selectinload(QuoteRequest.variant),
            )
            .order_by(desc(QuoteRequest.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_quotes(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(QuoteRequest))
        return int(result.scalar_one())
