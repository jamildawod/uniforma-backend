"""add pim import system

Revision ID: 20260313_000007
Revises: 20260313_000006
Create Date: 2026-03-13 00:00:07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260313_000007"
down_revision = "20260313_000006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE pim_source_type_enum ADD VALUE IF NOT EXISTS 'sftp'")
    op.execute("ALTER TYPE pim_source_type_enum ADD VALUE IF NOT EXISTS 'http'")
    op.execute("ALTER TYPE pim_source_type_enum ADD VALUE IF NOT EXISTS 'local'")

    op.add_column("pim_sources", sa.Column("host", sa.String(length=255), nullable=True))
    op.add_column("pim_sources", sa.Column("port", sa.Integer(), nullable=True))
    op.add_column("pim_sources", sa.Column("username", sa.String(length=255), nullable=True))
    op.add_column("pim_sources", sa.Column("password", sa.String(length=255), nullable=True))
    op.add_column("pim_sources", sa.Column("path", sa.String(length=1024), nullable=True))
    op.add_column("pim_sources", sa.Column("file_pattern", sa.String(length=255), nullable=True))
    op.add_column("pim_sources", sa.Column("schedule", sa.String(length=255), nullable=True))
    op.add_column("pim_sources", sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False))
    op.add_column(
        "pim_sources",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.execute(
        """
        UPDATE pim_sources
        SET path = COALESCE(config_json->>'path', config_json->>'url')
        """
    )
    op.execute(
        """
        UPDATE pim_sources
        SET host = config_json->>'host',
            port = NULLIF(config_json->>'port', '')::integer,
            username = config_json->>'username',
            password = config_json->>'password',
            file_pattern = config_json->>'file_pattern',
            schedule = config_json->>'schedule'
        WHERE config_json IS NOT NULL
        """
    )

    op.alter_column("pim_sources", "type", existing_type=sa.Enum(name="pim_source_type_enum"), nullable=False)
    op.drop_column("pim_sources", "config_json")

    op.create_table(
        "pim_import_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=64), server_default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_processed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_log", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["pim_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("pim_import_runs")

    op.add_column("pim_sources", sa.Column("config_json", sa.JSON(), nullable=True))
    op.execute(
        """
        UPDATE pim_sources
        SET config_json = json_build_object(
            'host', host,
            'port', port,
            'username', username,
            'password', password,
            'path', path,
            'file_pattern', file_pattern,
            'schedule', schedule
        )
        """
    )
    op.drop_column("pim_sources", "created_at")
    op.drop_column("pim_sources", "is_active")
    op.drop_column("pim_sources", "schedule")
    op.drop_column("pim_sources", "file_pattern")
    op.drop_column("pim_sources", "path")
    op.drop_column("pim_sources", "password")
    op.drop_column("pim_sources", "username")
    op.drop_column("pim_sources", "port")
    op.drop_column("pim_sources", "host")
