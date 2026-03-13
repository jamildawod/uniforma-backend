from app.models.quote_request import QuoteRequest
from app.repositories.quote_repository import QuoteRepository
from app.schemas.quote import QuoteRequestCreate, QuoteRequestRead


class QuoteService:
    def __init__(self, repository: QuoteRepository) -> None:
        self.repository = repository

    async def create_quote(self, payload: QuoteRequestCreate) -> QuoteRequestRead:
        quote_request = QuoteRequest(
            name=payload.name,
            email=str(payload.email),
            company=payload.company,
            message=payload.message,
            status="new",
        )
        created = await self.repository.create(quote_request)
        return QuoteRequestRead.model_validate(created)

    async def list_quotes(self, limit: int = 50, offset: int = 0) -> list[QuoteRequestRead]:
        quotes = await self.repository.list_quotes(limit=limit, offset=offset)
        return [QuoteRequestRead.model_validate(quote) for quote in quotes]

    async def count_quotes(self) -> int:
        return await self.repository.count_quotes()
