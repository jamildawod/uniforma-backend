from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_data_quality_service, get_pim_import_service
from app.db.session import get_db
from app.models.user import User
from app.schemas.pim import (
    PimConnectionTestResponse,
    PimImportRunRead,
    PimRunImportRequest,
    PimSourceCreateRequest,
    PimSourceRead,
)
from app.schemas.product import DataQualityResponse
from app.schemas.sync import PimSyncResponse
from app.services.data_quality_service import DataQualityService
from app.services.pim_import_service import PimImportService

router = APIRouter()


@router.get("/admin/pim/sources", response_model=list[PimSourceRead])
async def list_pim_sources(
    _: User = Depends(get_current_superuser),
    service: PimImportService = Depends(get_pim_import_service),
) -> list[PimSourceRead]:
    return [PimSourceRead.model_validate(source) for source in await service.list_sources()]


@router.post("/admin/pim/sources", response_model=PimSourceRead, status_code=status.HTTP_201_CREATED)
async def create_pim_source(
    payload: PimSourceCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
    service: PimImportService = Depends(get_pim_import_service),
) -> PimSourceRead:
    source = await service.create_source(payload.model_dump())
    await db.commit()
    return PimSourceRead.model_validate(source)


@router.post("/admin/pim/sources/{source_id}/test", response_model=PimConnectionTestResponse)
async def test_pim_source(
    source_id: int,
    _: User = Depends(get_current_superuser),
    service: PimImportService = Depends(get_pim_import_service),
) -> PimConnectionTestResponse:
    source = next((item for item in await service.list_sources() if item.id == source_id), None)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PIM source not found.")
    return PimConnectionTestResponse(ok=await service.test_source_connection(source))


@router.post("/admin/pim/run-import", response_model=PimSyncResponse)
async def run_pim_import(
    payload: PimRunImportRequest,
    _: User = Depends(get_current_superuser),
    service: PimImportService = Depends(get_pim_import_service),
) -> PimSyncResponse:
    source = next((item for item in await service.list_sources() if item.id == payload.source_id), None)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PIM source not found.")
    result = await service.run_import(source)
    response = result.sync.model_copy()
    response.records_processed = result.processed
    response.records_created = result.created
    response.records_updated = result.updated
    return response


@router.get("/admin/pim/imports", response_model=list[PimImportRunRead])
async def list_pim_import_runs(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(get_current_superuser),
    service: PimImportService = Depends(get_pim_import_service),
) -> list[PimImportRunRead]:
    return [PimImportRunRead.model_validate(run) for run in await service.list_import_runs(limit=limit)]


@router.get("/admin/pim/data-quality", response_model=DataQualityResponse)
async def get_pim_data_quality(
    _: User = Depends(get_current_superuser),
    service: DataQualityService = Depends(get_data_quality_service),
) -> DataQualityResponse:
    return await service.get_issues()
