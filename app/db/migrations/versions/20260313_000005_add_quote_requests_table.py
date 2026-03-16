"""add quote requests table

Revision ID: 20260313_000005
Revises: 20260312_000004
Create Date: 2026-03-13 00:00:05
"""

from alembic import op
import sqlalchemy as sa


revision = "20260313_000005"
down_revision = "20260312_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quote_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=64), server_default="new", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quote_requests_email", "quote_requests", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_quote_requests_email", table_name="quote_requests")
    op.drop_table("quote_requests")
