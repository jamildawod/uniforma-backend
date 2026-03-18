"""backend audit fixes

Revision ID: 20260318_000006
Revises: 20260317_000005
Create Date: 2026-03-18 00:00:06
"""

from alembic import op
import sqlalchemy as sa


revision = "20260318_000006"
down_revision = "20260317_000005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── suppliers ──────────────────────────────────────────────────────────────
    # Table may already exist with a different schema (slug-based).
    # Create it only if it is truly missing.
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id         SERIAL PRIMARY KEY,
            code       VARCHAR(64)              NOT NULL DEFAULT '',
            name       VARCHAR(255)             NOT NULL,
            is_active  BOOLEAN                  NOT NULL DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """))

    # Add 'code' column if the table existed with old schema (had 'slug' instead)
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='suppliers' AND column_name='code'
            ) THEN
                ALTER TABLE suppliers ADD COLUMN code VARCHAR(64) NOT NULL DEFAULT '';
            END IF;
        END$$;
    """))

    # Populate code from slug if code is still blank
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='suppliers' AND column_name='slug'
            ) THEN
                UPDATE suppliers SET code = slug WHERE code = '' OR code IS NULL;
            END IF;
        END$$;
    """))

    # Add 'is_active' column if missing
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='suppliers' AND column_name='is_active'
            ) THEN
                ALTER TABLE suppliers ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
            END IF;
        END$$;
    """))

    # Populate is_active from sync_enabled if that column exists
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='suppliers' AND column_name='sync_enabled'
            ) THEN
                UPDATE suppliers SET is_active = sync_enabled;
            END IF;
        END$$;
    """))

    # Unique index on code
    conn.execute(sa.text(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_suppliers_code ON suppliers (code)"
    ))

    # ── categories.image ───────────────────────────────────────────────────────
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='categories' AND column_name='image'
            ) THEN
                ALTER TABLE categories ADD COLUMN image VARCHAR(1024);
            END IF;
        END$$;
    """))

    # ── products.supplier_id ───────────────────────────────────────────────────
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='products' AND column_name='supplier_id'
            ) THEN
                ALTER TABLE products ADD COLUMN supplier_id INTEGER;
            END IF;
        END$$;
    """))

    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name='fk_products_supplier_id_suppliers'
            ) THEN
                ALTER TABLE products
                    ADD CONSTRAINT fk_products_supplier_id_suppliers
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                    ON DELETE SET NULL;
            END IF;
        END$$;
    """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_products_category_id ON products (category_id)"
    ))

    # ── sync_runs extra columns ────────────────────────────────────────────────
    for col_def in [
        ("supplier_id",    "INTEGER"),
        ("rows_processed", "INTEGER NOT NULL DEFAULT 0"),
        ("rows_created",   "INTEGER NOT NULL DEFAULT 0"),
        ("rows_updated",   "INTEGER NOT NULL DEFAULT 0"),
        ("rows_failed",    "INTEGER NOT NULL DEFAULT 0"),
    ]:
        col, typedef = col_def
        conn.execute(sa.text(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='sync_runs' AND column_name='{col}'
                ) THEN
                    ALTER TABLE sync_runs ADD COLUMN {col} {typedef};
                END IF;
            END$$;
        """))

    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name='fk_sync_runs_supplier_id_suppliers'
            ) THEN
                ALTER TABLE sync_runs
                    ADD CONSTRAINT fk_sync_runs_supplier_id_suppliers
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                    ON DELETE SET NULL;
            END IF;
        END$$;
    """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_sync_runs_supplier_id ON sync_runs (supplier_id)"
    ))

    # ── ingestion_logs ─────────────────────────────────────────────────────────
    # Table may already exist with a legacy schema — add missing columns only.
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS ingestion_logs (
            id             SERIAL PRIMARY KEY,
            supplier_id    INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
            sync_run_id    INTEGER REFERENCES sync_runs(id) ON DELETE SET NULL,
            started_at     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            finished_at    TIMESTAMP WITH TIME ZONE,
            status         VARCHAR(32) NOT NULL DEFAULT 'running',
            rows_processed INTEGER NOT NULL DEFAULT 0,
            rows_created   INTEGER NOT NULL DEFAULT 0,
            rows_updated   INTEGER NOT NULL DEFAULT 0,
            rows_failed    INTEGER NOT NULL DEFAULT 0,
            error_message  TEXT
        )
    """))

    # Add columns that may be missing if table existed with old schema
    for col, typedef in [
        ("sync_run_id",    "INTEGER REFERENCES sync_runs(id) ON DELETE SET NULL"),
        ("started_at",     "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()"),
        ("finished_at",    "TIMESTAMP WITH TIME ZONE"),
        ("status",         "VARCHAR(32) NOT NULL DEFAULT 'running'"),
        ("rows_processed", "INTEGER NOT NULL DEFAULT 0"),
        ("rows_created",   "INTEGER NOT NULL DEFAULT 0"),
        ("rows_updated",   "INTEGER NOT NULL DEFAULT 0"),
        ("rows_failed",    "INTEGER NOT NULL DEFAULT 0"),
        ("error_message",  "TEXT"),
    ]:
        conn.execute(sa.text(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='ingestion_logs' AND column_name='{col}'
                ) THEN
                    ALTER TABLE ingestion_logs ADD COLUMN {col} {typedef};
                END IF;
            END$$;
        """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_ingestion_logs_supplier_id  ON ingestion_logs (supplier_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_ingestion_logs_sync_run_id  ON ingestion_logs (sync_run_id)"
    ))

    # ── seed data ──────────────────────────────────────────────────────────────
    # Build INSERT dynamically: old schema has NOT NULL slug, new schema doesn't.
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='suppliers' AND column_name='slug'
            ) THEN
                INSERT INTO suppliers (code, name, is_active, slug)
                VALUES ('hejco', 'Hejco', true, 'hejco')
                ON CONFLICT (code) DO NOTHING;
            ELSE
                INSERT INTO suppliers (code, name, is_active)
                VALUES ('hejco', 'Hejco', true)
                ON CONFLICT (code) DO NOTHING;
            END IF;
        END$$;
    """))

    conn.execute(sa.text("""
        UPDATE products
        SET supplier_id = suppliers.id
        FROM suppliers
        WHERE suppliers.code = 'hejco'
          AND products.supplier_id IS NULL
    """))

    conn.execute(sa.text("""
        UPDATE sync_runs
        SET supplier_id = suppliers.id
        FROM suppliers
        WHERE suppliers.code = 'hejco'
          AND sync_runs.supplier_id IS NULL
    """))

    # ── product_variants expression indexes ───────────────────────────────────
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_product_variants_lower_color ON product_variants (lower(color))"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_product_variants_lower_size  ON product_variants (lower(size))"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_product_variants_lower_size"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_product_variants_lower_color"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_ingestion_logs_sync_run_id"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_ingestion_logs_supplier_id"))
    conn.execute(sa.text("DROP TABLE IF EXISTS ingestion_logs"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_sync_runs_supplier_id"))
    conn.execute(sa.text("ALTER TABLE sync_runs DROP CONSTRAINT IF EXISTS fk_sync_runs_supplier_id_suppliers"))
    conn.execute(sa.text("ALTER TABLE sync_runs DROP COLUMN IF EXISTS rows_failed"))
    conn.execute(sa.text("ALTER TABLE sync_runs DROP COLUMN IF EXISTS rows_updated"))
    conn.execute(sa.text("ALTER TABLE sync_runs DROP COLUMN IF EXISTS rows_created"))
    conn.execute(sa.text("ALTER TABLE sync_runs DROP COLUMN IF EXISTS rows_processed"))
    conn.execute(sa.text("ALTER TABLE sync_runs DROP COLUMN IF EXISTS supplier_id"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_products_category_id"))
    conn.execute(sa.text("ALTER TABLE products DROP CONSTRAINT IF EXISTS fk_products_supplier_id_suppliers"))
    conn.execute(sa.text("ALTER TABLE products DROP COLUMN IF EXISTS supplier_id"))
    conn.execute(sa.text("ALTER TABLE categories DROP COLUMN IF EXISTS image"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_suppliers_code"))
    conn.execute(sa.text("DROP TABLE IF EXISTS suppliers"))
