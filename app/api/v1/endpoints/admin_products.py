import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_product_read_service
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.admin_override_repository import AdminOverrideRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import AdminImageCreateRequest, AdminOverridePatchRequest, AdminProductRead
from app.schemas.sync import PimSyncResponse
from app.services.ftp_image_service import FtpImageService
from app.services.pim_ingestion_service import PimIngestionService
from app.services.pim_sync_service import PimSyncService
from app.services.product_read_service import ProductReadService

router = APIRouter()


@router.get("/admin/products", response_model=list[AdminProductRead])
async def list_admin_products(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_superuser),
    service: ProductReadService = Depends(get_product_read_service),
) -> list[AdminProductRead]:
    return await service.list_admin_products(limit=limit, offset=offset)


@router.get("/admin/products/{product_id}", response_model=AdminProductRead)
async def get_admin_product(
    product_id: uuid.UUID,
    _: User = Depends(get_current_superuser),
    service: ProductReadService = Depends(get_product_read_service),
) -> AdminProductRead:
    product = await service.get_admin_product(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.patch("/admin/products/{product_id}", response_model=AdminProductRead)
async def patch_admin_product(
    product_id: uuid.UUID,
    payload: AdminOverridePatchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
) -> AdminProductRead:
    service = ProductReadService(
        ProductRepository(db),
        AdminOverrideRepository(db),
    )
    product = await service.patch_admin_product(product_id, payload, updated_by=user.email)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    await db.commit()
    return product


@router.post("/admin/products/{product_id}/image", response_model=AdminProductRead)
async def add_product_image(
    product_id: uuid.UUID,
    payload: AdminImageCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> AdminProductRead:
    service = ProductReadService(
        ProductRepository(db),
        AdminOverrideRepository(db),
    )
    product = await service.add_product_image(product_id, payload)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    await db.commit()
    return product


@router.post("/admin/sync/pim", response_model=PimSyncResponse)
async def sync_pim(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> PimSyncResponse:
    settings = get_settings()
    product_repository = ProductRepository(db)
    sync_service = PimSyncService(
        PimIngestionService(db, product_repository, settings),
        FtpImageService(db, product_repository, settings),
        settings,
    )
    return await sync_service.run_sync()
