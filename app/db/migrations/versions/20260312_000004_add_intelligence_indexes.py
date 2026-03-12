"""add intelligence indexes

Revision ID: 20260312_000004
Revises: 20260312_000003
Create Date: 2026-03-12 00:00:04
"""

from alembic import op


revision = "20260312_000004"
down_revision = "20260312_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_products_deleted_at", "products", ["deleted_at"], unique=False)
    op.create_index("ix_products_brand", "products", ["brand"], unique=False)
    op.create_index("ix_product_variants_ean", "product_variants", ["ean"], unique=False)
    op.create_index("ix_product_variants_stock_quantity", "product_variants", ["stock_quantity"], unique=False)
    op.create_index("ix_admin_overrides_product_id", "admin_overrides", ["product_id"], unique=False)
    op.create_index("ix_sync_runs_started_at", "sync_runs", ["started_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sync_runs_started_at", table_name="sync_runs")
    op.drop_index("ix_admin_overrides_product_id", table_name="admin_overrides")
    op.drop_index("ix_product_variants_stock_quantity", table_name="product_variants")
    op.drop_index("ix_product_variants_ean", table_name="product_variants")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_deleted_at", table_name="products")
