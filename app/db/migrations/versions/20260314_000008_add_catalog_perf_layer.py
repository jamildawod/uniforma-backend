"""add catalog performance layer

Revision ID: 20260314_000008
Revises: 20260313_000007
Create Date: 2026-03-14 00:00:08
"""

from alembic import op


revision = "20260314_000008"
down_revision = "20260313_000007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_variants_color ON product_variants (color)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_variants_size ON product_variants (size)")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS product_name_trgm
        ON products
        USING gin (name gin_trgm_ops)
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS product_list_view AS
        SELECT
            p.id AS product_id,
            p.slug AS slug,
            p.name AS name,
            p.created_at AS created_at,
            c.name AS category,
            p.brand AS brand,
            MIN(v.price) FILTER (WHERE v.price IS NOT NULL) AS price,
            COALESCE(
                MAX(CASE WHEN pi.is_primary THEN pi.url END),
                MAX(pi.url)
            ) AS primary_image,
            COALESCE(
                ARRAY_REMOVE(ARRAY_AGG(DISTINCT v.color) FILTER (WHERE v.color IS NOT NULL), NULL),
                ARRAY[]::varchar[]
            ) AS colors,
            COALESCE(
                ARRAY_REMOVE(ARRAY_AGG(DISTINCT v.size) FILTER (WHERE v.size IS NOT NULL), NULL),
                ARRAY[]::varchar[]
            ) AS sizes
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN product_variants v
            ON v.product_id = p.id
           AND v.deleted_at IS NULL
           AND v.is_active = TRUE
        LEFT JOIN product_images pi ON pi.product_id = p.id
        WHERE p.deleted_at IS NULL
          AND p.status = 'active'
          AND p.is_active = TRUE
        GROUP BY p.id, p.slug, p.name, p.created_at, c.name, p.brand
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_product_list_view_product_id ON product_list_view (product_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_catalog_slug ON product_list_view (slug)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_catalog_category ON product_list_view (category)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_catalog_price ON product_list_view (price)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_catalog_created_category ON product_list_view (created_at, category)")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_product_list_view_name_trgm
        ON product_list_view
        USING gin (name gin_trgm_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_product_list_view_colors
        ON product_list_view
        USING gin (colors)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_product_list_view_sizes
        ON product_list_view
        USING gin (sizes)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_product_list_view_sizes")
    op.execute("DROP INDEX IF EXISTS ix_product_list_view_colors")
    op.execute("DROP INDEX IF EXISTS ix_product_list_view_name_trgm")
    op.execute("DROP INDEX IF EXISTS idx_catalog_created_category")
    op.execute("DROP INDEX IF EXISTS idx_catalog_category")
    op.execute("DROP INDEX IF EXISTS idx_catalog_price")
    op.execute("DROP INDEX IF EXISTS idx_catalog_slug")
    op.execute("DROP INDEX IF EXISTS idx_product_list_view_product_id")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS product_list_view")
    op.execute("DROP INDEX IF EXISTS product_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_product_variants_size")
    op.execute("DROP INDEX IF EXISTS ix_product_variants_color")
