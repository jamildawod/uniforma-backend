from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_catalog_service, get_product_read_service
from app.schemas.product import (
    CategoryTreeNode,
    ProductImageRead,
    ProductListFilters,
    ProductListResponse,
    ProductRead,
    ProductSearchResponse,
    ProductVariantRead,
    SearchResponse,
)
from app.services.catalog_service import CatalogService
from app.services.product_read_service import ProductReadService

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=10),
    service: CatalogService = Depends(get_catalog_service),
) -> SearchResponse:
    return await service.search_products(query=q, limit=limit)


@router.get("/products/search", response_model=ProductSearchResponse)
async def search_products_legacy(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: ProductReadService = Depends(get_product_read_service),
) -> ProductSearchResponse:
    return ProductSearchResponse(items=await service.search_public_products(query=q, limit=limit))


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    category: str | None = Query(default=None),
    color: str | None = Query(default=None),
    size: str | None = Query(default=None),
    search: str | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=24, ge=1, le=200),
    service: CatalogService = Depends(get_catalog_service),
) -> ProductListResponse:
    return await service.list_products(
        category=category,
        color=color,
        size=size,
        search=search,
        cursor=cursor,
        limit=limit,
    )


@router.get("/categories", response_model=list[CategoryTreeNode])
async def list_categories(
    service: CatalogService = Depends(get_catalog_service),
) -> list[CategoryTreeNode]:
    return [CategoryTreeNode.model_validate(item) for item in await service.list_categories()]


@router.get("/filters", response_model=ProductListFilters)
async def list_filters(
    service: CatalogService = Depends(get_catalog_service),
) -> ProductListFilters:
    return await service.list_filters()


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
