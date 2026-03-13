import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_is_active_deleted_at", "is_active", "deleted_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    external_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="product_status_enum"),
        nullable=False,
        default=ProductStatus.draft,
        server_default=ProductStatus.draft.value,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    category: Mapped["Category | None"] = relationship(back_populates="products")
    brand_rel: Mapped["Brand | None"] = relationship(back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    admin_overrides: Mapped[list["AdminOverride"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    attribute_values: Mapped[list["ProductAttributeValue"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
