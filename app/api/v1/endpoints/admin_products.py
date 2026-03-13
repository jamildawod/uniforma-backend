import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_product_read_service, get_product_service, get_quote_service
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.admin_override_repository import AdminOverrideRepository
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.intelligence import SyncRun as SyncRunRead
from app.schemas.product import (
    AdminImageCreateRequest,
    AdminOverridePatchRequest,
    AdminProductCreateRequest,
    AdminProductPublishRequest,
    AdminProductRead,
    AdminProductUpdateRequest,
    AdminUploadResponse,
)
from app.schemas.quote import QuoteRequestRead
from app.schemas.sync import PimSyncResponse
from app.services.ftp_image_service import FtpImageService
from app.services.pim_ingestion_service import PimIngestionService
from app.services.pim_sync_service import PimSyncService
from app.services.product_service import ProductService
from app.services.product_read_service import ProductReadService
from app.services.quote_service import QuoteService

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


@router.post("/admin/products", response_model=AdminProductRead, status_code=status.HTTP_201_CREATED)
async def create_admin_product(
    payload: AdminProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
    service: ProductService = Depends(get_product_service),
) -> AdminProductRead:
    product = await service.create_admin_product(payload)
    await db.commit()
    return product


@router.put("/admin/products/{product_id}", response_model=AdminProductRead)
async def update_admin_product(
    product_id: uuid.UUID,
    payload: AdminProductUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
    service: ProductService = Depends(get_product_service),
) -> AdminProductRead:
    product = await service.update_admin_product(product_id, payload)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    await db.commit()
    return product


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
    service: ProductService = Depends(get_product_service),
) -> None:
    product = await service.delete_admin_product(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    await db.commit()


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


@router.post("/admin/products/{product_id}/publish", response_model=AdminProductRead)
async def publish_admin_product(
    product_id: uuid.UUID,
    payload: AdminProductPublishRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
    service: ProductService = Depends(get_product_service),
) -> AdminProductRead:
    product = await service.set_product_publication(product_id, payload.is_active)
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


@router.post("/admin/upload", response_model=AdminUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_admin_image(
    file: UploadFile = File(...),
    _: User = Depends(get_current_superuser),
) -> AdminUploadResponse:
    settings = get_settings()
    upload_root = settings.uploads_root
    upload_root.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "upload").suffix.lower()
    filename = f"{uuid.uuid4().hex}{suffix}"
    destination = upload_root / filename
    contents = await file.read()
    destination.write_bytes(contents)
    return AdminUploadResponse(filename=filename, url=f"/uploads/{filename}")


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


@router.get("/admin/sync/runs", response_model=list[SyncRunRead])
async def list_sync_runs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> list[SyncRunRead]:
    repository = IntelligenceRepository(db)
    runs = await repository.fetch_recent_sync_runs(limit=limit, offset=offset)
    return [SyncRunRead(**run) for run in runs]


@router.get("/admin/quotes", response_model=list[QuoteRequestRead])
async def list_admin_quotes(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_superuser),
    service: QuoteService = Depends(get_quote_service),
) -> list[QuoteRequestRead]:
    return await service.list_quotes(limit=limit, offset=offset)
