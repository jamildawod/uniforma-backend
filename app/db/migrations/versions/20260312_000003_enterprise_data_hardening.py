"""enterprise data hardening

Revision ID: 20260312_000003
Revises: 20260312_000002
Create Date: 2026-03-12 00:00:03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260312_000003"
down_revision = "20260312_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("products", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_products_is_active_deleted_at",
        "products",
        ["is_active", "deleted_at"],
        unique=False,
    )

    op.add_column("product_variants", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("product_variants", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_product_variants_is_active_deleted_at",
        "product_variants",
        ["is_active", "deleted_at"],
        unique=False,
    )
    op.create_index(
        "ix_product_variants_product_id",
        "product_variants",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        "ix_product_images_product_id",
        "product_images",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("products_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("products_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("variants_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("variants_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("images_synced", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="success", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sync_runs")
    op.drop_index("ix_product_images_product_id", table_name="product_images")
    op.drop_index("ix_product_variants_product_id", table_name="product_variants")
    op.drop_index("ix_product_variants_is_active_deleted_at", table_name="product_variants")
    op.drop_column("product_variants", "deleted_at")
    op.drop_column("product_variants", "last_seen_at")
    op.drop_index("ix_products_is_active_deleted_at", table_name="products")
    op.drop_column("products", "deleted_at")
    op.drop_column("products", "last_seen_at")
