import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ProductStatusValue = Literal["draft", "active", "archived"]
AttributeTypeValue = Literal["text", "number", "select", "boolean"]


class BrandRead(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: str | None

    model_config = ConfigDict(from_attributes=True)


class BrandCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    logo_url: str | None = Field(default=None, max_length=1024)


class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: int | None
    position: int

    model_config = ConfigDict(from_attributes=True)


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    parent_id: int | None = None
    position: int = 0


class ProductImageRead(BaseModel):
    id: int
    variant_id: int | None
    url: str
    position: int
    is_primary: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductVariantRead(BaseModel):
    id: int
    sku: str
    ean: str | None
    color: str | None
    size: str | None
    price: Decimal | None
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AttributeRead(BaseModel):
    id: int
    name: str
    type: AttributeTypeValue

    model_config = ConfigDict(from_attributes=True)


class AttributeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: AttributeTypeValue


class ProductAttributeValueRead(BaseModel):
    attribute_id: int
    value: str
    attribute: AttributeRead

    model_config = ConfigDict(from_attributes=True)


class ProductRead(BaseModel):
    id: uuid.UUID
    external_id: str
    name: str
    slug: str
    description: str | None
    status: ProductStatusValue
    brand_id: int | None
    brand: BrandRead | None = None
    category_id: int | None
    category: CategoryRead | None = None
    image_url: str | None = None
    is_active: bool
    deleted_at: datetime | None = None
    last_seen_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageRead] = Field(default_factory=list)
    variants: list[ProductVariantRead] = Field(default_factory=list)
    attributes: list[ProductAttributeValueRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductSearchResponse(BaseModel):
    items: list[ProductRead]


class CatalogProductSummary(BaseModel):
    product_id: uuid.UUID
    slug: str
    name: str
    created_at: datetime
    category: str | None = None
    brand: str | None = None
    price: Decimal | None = None
    primary_image: str | None = None
    colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)


class FilterOption(BaseModel):
    value: str
    count: int


class ProductListFilters(BaseModel):
    categories: list[FilterOption] = Field(default_factory=list)
    colors: list[FilterOption] = Field(default_factory=list)
    sizes: list[FilterOption] = Field(default_factory=list)


class ProductListResponse(BaseModel):
    products: list[CatalogProductSummary] = Field(default_factory=list)
    next_cursor: str | None = None
    filters: ProductListFilters = Field(default_factory=ProductListFilters)


class SearchMatch(BaseModel):
    product_id: uuid.UUID
    slug: str
    name: str
    category: str | None = None
    primary_image: str | None = None
    price: Decimal | None = None
    score: float


class SearchResponse(BaseModel):
    items: list[SearchMatch] = Field(default_factory=list)


class CategoryTreeNode(BaseModel):
    id: int
    name: str
    slug: str
    children: list["CategoryTreeNode"] = Field(default_factory=list)


class AdminOverridePatchRequest(BaseModel):
    overrides: dict[str, str | int | float | bool | None]


class AdminImageCreateRequest(BaseModel):
    url: str = Field(min_length=1, max_length=1024)
    variant_id: int | None = None
    is_primary: bool = False
    position: int = 0


class AdminVariantCreateRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=128)
    ean: str | None = Field(default=None, max_length=64)
    size: str | None = Field(default=None, max_length=64)
    color: str | None = Field(default=None, max_length=64)
    price: Decimal | None = None
    stock_quantity: int = 0
    is_active: bool = True


class AdminProductAttributeValueInput(BaseModel):
    attribute_id: int
    value: str = Field(min_length=1)


class AdminProductRead(ProductRead):
    applied_overrides: dict[str, str | int | float | bool | list | dict | None] = Field(default_factory=dict)


class AdminProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    brand_id: int | None = None
    category_id: int | None = None
    status: ProductStatusValue = "draft"
    image_url: str | None = Field(default=None, max_length=1024)
    is_active: bool = True
    variants: list[AdminVariantCreateRequest] = Field(default_factory=list)
    attributes: list[AdminProductAttributeValueInput] = Field(default_factory=list)


class AdminProductUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    brand_id: int | None = None
    category_id: int | None = None
    status: ProductStatusValue = "draft"
    image_url: str | None = Field(default=None, max_length=1024)
    is_active: bool = True
    attributes: list[AdminProductAttributeValueInput] = Field(default_factory=list)


class AdminProductPublishRequest(BaseModel):
    is_active: bool


class AdminUploadResponse(BaseModel):
    filename: str
    url: str


class MediaItemRead(BaseModel):
    filename: str
    url: str


class DataQualityIssue(BaseModel):
    key: str
    label: str
    count: int


class DataQualityResponse(BaseModel):
    issues: list[DataQualityIssue] = Field(default_factory=list)


CategoryTreeNode.model_rebuild()
