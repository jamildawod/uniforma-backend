from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_product_read_service, get_product_service
from app.schemas.product import ProductRead, ProductVariantRead
from app.services.product_read_service import ProductReadService
from app.services.product_service import ProductService

router = APIRouter()


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    service: ProductReadService = Depends(get_product_read_service),
) -> list[ProductRead]:
    return await service.list_public_products(limit=limit, offset=offset)


@router.get("/products/{product_identifier}", response_model=ProductRead)
async def get_product(
    product_identifier: str,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    product = await service.get_public_product_by_identifier(product_identifier)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.get("/products/{product_identifier}/variants", response_model=list[ProductVariantRead])
async def get_product_variants(
    product_identifier: str,
    service: ProductService = Depends(get_product_service),
) -> list[ProductVariantRead]:
    product = await service.get_public_product_by_identifier(product_identifier)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product.variants
