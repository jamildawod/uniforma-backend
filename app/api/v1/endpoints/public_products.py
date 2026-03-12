from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_product_read_service
from app.schemas.product import ProductRead, ProductVariantRead
from app.services.product_read_service import ProductReadService

router = APIRouter()


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    service: ProductReadService = Depends(get_product_read_service),
) -> list[ProductRead]:
    return await service.list_public_products(limit=limit, offset=offset)


@router.get("/products/{slug}", response_model=ProductRead)
async def get_product(
    slug: str,
    service: ProductReadService = Depends(get_product_read_service),
) -> ProductRead:
    product = await service.get_public_product(slug)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.get("/products/{slug}/variants", response_model=list[ProductVariantRead])
async def get_product_variants(
    slug: str,
    service: ProductReadService = Depends(get_product_read_service),
) -> list[ProductVariantRead]:
    variants = await service.get_public_variants(slug)
    if variants is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return variants
