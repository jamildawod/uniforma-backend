"""expand to full pim

Revision ID: 20260313_000006
Revises: 20260313_000005
Create Date: 2026-03-13 00:00:06
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op


revision = "20260313_000006"
down_revision = "20260313_000005"
branch_labels = None
depends_on = None


product_status_enum = postgresql.ENUM(
    "draft",
    "active",
    "archived",
    name="product_status_enum",
    create_type=False,
)
attribute_type_enum = postgresql.ENUM(
    "text",
    "number",
    "select",
    "boolean",
    name="attribute_type_enum",
    create_type=False,
)
pim_source_type_enum = postgresql.ENUM(
    "csv",
    "ftp",
    "api",
    name="pim_source_type_enum",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    product_status_enum.create(bind, checkfirst=True)
    attribute_type_enum.create(bind, checkfirst=True)
    pim_source_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.String(length=1024), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_brands_slug", "brands", ["slug"], unique=True)

    op.add_column("categories", sa.Column("position", sa.Integer(), server_default="0", nullable=False))

    op.add_column("products", sa.Column("brand_id", sa.Integer(), nullable=True))
    op.add_column(
        "products",
        sa.Column("status", product_status_enum, server_default="draft", nullable=False),
    )
    op.create_foreign_key("fk_products_brand_id_brands", "products", "brands", ["brand_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_products_brand_id", "products", ["brand_id"], unique=False)
    op.create_index("ix_products_status", "products", ["status"], unique=False)
    op.execute(
        """
        UPDATE products
        SET status = CASE
            WHEN deleted_at IS NOT NULL THEN 'archived'::product_status_enum
            WHEN is_active = true THEN 'active'::product_status_enum
            ELSE 'draft'::product_status_enum
        END
        """
    )

    op.add_column("product_images", sa.Column("url", sa.String(length=1024), server_default="", nullable=False))
    op.add_column("product_images", sa.Column("position", sa.Integer(), server_default="0", nullable=False))
    op.add_column(
        "product_images",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.execute("UPDATE product_images SET url = external_path, position = sort_order")

    op.create_table(
        "attributes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", attribute_type_enum, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "product_attribute_values",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attribute_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["attribute_id"], ["attributes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id", "attribute_id", name="pk_product_attribute_values"),
    )

    op.create_table(
        "pim_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", pim_source_type_enum, nullable=False),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "pim_sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=64), server_default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_imported", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["pim_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("quote_requests", sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("quote_requests", sa.Column("variant_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_quote_requests_product_id_products", "quote_requests", "products", ["product_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_quote_requests_variant_id_product_variants", "quote_requests", "product_variants", ["variant_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_quote_requests_variant_id_product_variants", "quote_requests", type_="foreignkey")
    op.drop_constraint("fk_quote_requests_product_id_products", "quote_requests", type_="foreignkey")
    op.drop_column("quote_requests", "variant_id")
    op.drop_column("quote_requests", "product_id")

    op.drop_table("pim_sync_runs")
    op.drop_table("pim_sources")
    op.drop_table("product_attribute_values")
    op.drop_table("attributes")

    op.drop_column("product_images", "created_at")
    op.drop_column("product_images", "position")
    op.drop_column("product_images", "url")

    op.drop_index("ix_products_status", table_name="products")
    op.drop_index("ix_products_brand_id", table_name="products")
    op.drop_constraint("fk_products_brand_id_brands", "products", type_="foreignkey")
    op.drop_column("products", "status")
    op.drop_column("products", "brand_id")

    op.drop_column("categories", "position")

    op.drop_index("ix_brands_slug", table_name="brands")
    op.drop_table("brands")

    bind = op.get_bind()
    pim_source_type_enum.drop(bind, checkfirst=True)
    attribute_type_enum.drop(bind, checkfirst=True)
    product_status_enum.drop(bind, checkfirst=True)
