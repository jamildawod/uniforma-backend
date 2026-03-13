from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_quote_service
from app.db.session import get_db
from app.schemas.quote import QuoteRequestCreate, QuoteRequestRead
from app.services.quote_service import QuoteService

router = APIRouter()


@router.post("/quotes", response_model=QuoteRequestRead, status_code=status.HTTP_201_CREATED)
async def create_quote(
    payload: QuoteRequestCreate,
    db: AsyncSession = Depends(get_db),
    service: QuoteService = Depends(get_quote_service),
) -> QuoteRequestRead:
    quote = await service.create_quote(payload)
    await db.commit()
    return quote


@router.get("/quotes", response_model=list[QuoteRequestRead])
async def list_quotes(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: QuoteService = Depends(get_quote_service),
) -> list[QuoteRequestRead]:
    return await service.list_quotes(limit=limit, offset=offset)
