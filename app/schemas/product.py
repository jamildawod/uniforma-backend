import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: int | None

    model_config = ConfigDict(from_attributes=True)


class ProductImageRead(BaseModel):
    id: int
    variant_id: int | None
    external_path: str
    local_path: str | None
    is_primary: bool
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class ProductVariantRead(BaseModel):
    id: int
    sku: str
    ean: str | None
    color: str | None
    size: str | None
    price: Decimal | None
    currency: str | None
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductRead(BaseModel):
    id: uuid.UUID
    external_id: str
    name: str
    slug: str
    description: str | None
    brand: str | None
    is_active: bool
    image_url: str | None = None
    deleted_at: datetime | None = None
    last_seen_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    category: CategoryRead | None = None
    images: list[ProductImageRead] = Field(default_factory=list)
    variants: list[ProductVariantRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AdminOverridePatchRequest(BaseModel):
    overrides: dict[str, str | int | float | bool | None]


class AdminImageCreateRequest(BaseModel):
    external_path: str
    local_path: str | None = None
    variant_id: int | None = None
    is_primary: bool = False
    sort_order: int = 0


class AdminProductRead(ProductRead):
    applied_overrides: dict[str, str | int | float | bool | list | dict | None] = Field(
        default_factory=dict,
    )


class AdminProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    brand: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=1024)
    is_active: bool = True


class AdminProductUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = None
    brand: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=1024)
    is_active: bool = True


class AdminProductPublishRequest(BaseModel):
    is_active: bool


class AdminUploadResponse(BaseModel):
    filename: str
    url: str
