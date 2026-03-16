"""add integration settings

Revision ID: 20260315_000009
Revises: 20260314_000008
Create Date: 2026-03-15 00:00:09
"""

from alembic import op
import sqlalchemy as sa


revision = "20260315_000009"
down_revision = "20260314_000008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("ftp_host", sa.String(length=255), nullable=True),
        sa.Column("ftp_username", sa.String(length=255), nullable=True),
        sa.Column("ftp_password_encrypted", sa.Text(), nullable=True),
        sa.Column("pictures_path", sa.String(length=1024), server_default="/Hejco/Pictures/jpeg", nullable=False),
        sa.Column(
            "product_data_path",
            sa.String(length=1024),
            server_default="/Hejco/product_data/Swedish/PIMexport_Hejco_sv-SE.csv",
            nullable=False,
        ),
        sa.Column("stock_path", sa.String(length=1024), server_default="/Hejco/stock_availability", nullable=False),
        sa.Column("sync_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sync_hour", sa.Integer(), server_default="3", nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), server_default="60", nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_status", sa.String(length=64), nullable=True),
        sa.Column("last_sync_message", sa.Text(), nullable=True),
        sa.Column("last_imported_product_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_integration_settings_provider", "integration_settings", ["provider"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_integration_settings_provider", table_name="integration_settings")
    op.drop_table("integration_settings")
