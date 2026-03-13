from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_product_read_service
from app.schemas.product import ProductImageRead, ProductRead, ProductSearchResponse, ProductVariantRead
from app.services.product_read_service import ProductReadService

router = APIRouter()


@router.get("/products/search", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: ProductReadService = Depends(get_product_read_service),
) -> ProductSearchResponse:
    return ProductSearchResponse(items=await service.search_public_products(query=q, limit=limit))


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: ProductReadService = Depends(get_product_read_service),
) -> list[ProductRead]:
    return await service.list_public_products(limit=limit, offset=offset)


@router.get("/products/{product_identifier}", response_model=ProductRead)
async def get_product(
    product_identifier: str,
    service: ProductReadService = Depends(get_product_read_service),
) -> ProductRead:
    product = await service.get_public_product(product_identifier)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.get("/products/{product_identifier}/variants", response_model=list[ProductVariantRead])
async def get_product_variants(
    product_identifier: str,
    service: ProductReadService = Depends(get_product_read_service),
) -> list[ProductVariantRead]:
    variants = await service.get_public_variants(product_identifier)
    if variants is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return variants


@router.get("/products/{product_identifier}/images", response_model=list[ProductImageRead])
async def get_product_images(
    product_identifier: str,
    service: ProductReadService = Depends(get_product_read_service),
) -> list[ProductImageRead]:
    images = await service.get_public_images(product_identifier)
    if images is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return images
