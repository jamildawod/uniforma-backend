from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser
from app.db.session import get_db
from app.models.user import User
from app.repositories.intelligence_repository import IntelligenceRepository
from app.schemas.intelligence import (
    DataQualityResponse,
    OverrideConflictResponse,
    SyncHealthResponse,
    SystemHealthResponse,
)
from app.services.admin_intelligence_service import AdminIntelligenceService

router = APIRouter()


def get_admin_intelligence_service(db: AsyncSession) -> AdminIntelligenceService:
    return AdminIntelligenceService(IntelligenceRepository(db))


@router.get("/admin/intelligence/summary", response_model=SystemHealthResponse)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> SystemHealthResponse:
    return await get_admin_intelligence_service(db).get_system_health()


@router.get("/admin/intelligence/data-quality", response_model=DataQualityResponse)
async def get_data_quality(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> DataQualityResponse:
    return await get_admin_intelligence_service(db).get_data_quality()


@router.get("/admin/intelligence/sync-health", response_model=SyncHealthResponse)
async def get_sync_health(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> SyncHealthResponse:
    return await get_admin_intelligence_service(db).get_sync_health(page=page, page_size=page_size)


@router.get("/admin/intelligence/override-conflicts", response_model=OverrideConflictResponse)
async def get_override_conflicts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> OverrideConflictResponse:
    return await get_admin_intelligence_service(db).get_override_conflicts(page=page, page_size=page_size)
