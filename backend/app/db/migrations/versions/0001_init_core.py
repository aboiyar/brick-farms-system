from alembic import op
import sqlalchemy as sa
from geoalchemy2.types import Geometry
from sqlalchemy.dialects import postgresql
import os
    # Create extensions where available. Some test/dev images may not have the
    # TimescaleDB extension packages installed; we allow skipping timescaledb
    # during local development by setting the SKIP_TIMESCALE env var. This
    # prevents CREATE EXTENSION from aborting the surrounding transaction when
    # the extension control file is missing.
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    except Exception:
        pass

    if not os.environ.get('SKIP_TIMESCALE'):
        try:
            op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
        except Exception:
            # If TimescaleDB isn't available the error is ignored and the
            # migration continues. However, some database images won't include
            # the extension; for local dev set SKIP_TIMESCALE=1 to skip this
            # step entirely.
            pass

    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    except Exception:
        pass
        # Try to create extensions where available. Run as a PL/pgSQL DO block
        # so errors (for missing extension control files) are handled inside the
        # database and do not abort the outer transaction. This allows migrations
        # to proceed even when TimescaleDB isn't installed in the image.
        op.execute("""DO $$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS postgis;
    EXCEPTION WHEN OTHERS THEN
        -- ignore
    END;
    BEGIN
        CREATE EXTENSION IF NOT EXISTS timescaledb;
    EXCEPTION WHEN OTHERS THEN
        -- ignore
    END;
    BEGIN
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
    EXCEPTION WHEN OTHERS THEN
        -- ignore
    END;
END;
$$;""")

    # Helper: tenant_id GUC (used by RLS policies)
    op.execute("""
    CREATE OR REPLACE FUNCTION app_current_tenant() RETURNS uuid AS $$
      SELECT nullif(current_setting('app.tenant_id', true), '')::uuid;
    $$ LANGUAGE SQL STABLE;
    """)

    # Enums
    crop_category = sa.Enum('crop','tree', name='crop_category')
    crop_category.create(op.get_bind(), checkfirst=True)
    stock_tx_type = sa.Enum('receive','issue','adjust', name='stock_tx_type')
    stock_tx_type.create(op.get_bind(), checkfirst=True)
    acct_type = sa.Enum('asset','liability','equity','income','expense', name='acct_type')
    acct_type.create(op.get_bind(), checkfirst=True)

    # Tenants & users
    op.create_table("tenant",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="enterprise")
    )
    op.create_table("membership",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="admin")
    )
    op.create_table("user",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("role", sa.String(50), nullable=False, server_default="admin")
    )

    # Farm and plots
    op.create_table("farm",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("state", sa.String(100)),
        sa.Column("lga", sa.String(100))
    )
    op.create_table("fieldplot",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POLYGON", srid=4326), nullable=False),
        sa.Column("area_ha", sa.Numeric(10,2)),
        sa.Column("soil_type", sa.String(120)),
        sa.Column("irrigation", sa.String(120))
    )

    # Crops
    op.create_table("crop",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("category", crop_category, nullable=False),
        sa.Column("common_name", sa.String(120), nullable=False),
        sa.Column("scientific_name", sa.String(200)),
        sa.Column("descriptors", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )
    op.create_table("variety",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("crop_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("attributes", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )

    # Sensors
    op.create_table("sensordevice",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("plot_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("protocol", sa.String(20)),
        sa.Column("api_key", sa.String(64), nullable=False),
        sa.Column("location", Geometry(geometry_type="POINT", srid=4326))
    )
    op.create_table("sensor_readings",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("metric", sa.String(64), index=True),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("unit", sa.String(24)),
        sa.Column("timestamp", sa.TIMESTAMP(timezone=True), index=True, nullable=False),
        sa.Column("location", Geometry(geometry_type="POINT", srid=4326))
    )
    # Timescale hypertable (wrap in try/except in case TimescaleDB isn't present
    # in the database image used for local integration).
    # Create hypertable only when TimescaleDB is present and not skipped.
    if not os.environ.get('SKIP_TIMESCALE'):
        try:
            op.execute("SELECT create_hypertable('sensor_readings','timestamp', if_not_exists => TRUE)")
        except Exception:
            # If TimescaleDB isn't available the hypertable step is skipped.
            pass

    # Inventory
    op.create_table("item",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("descriptors", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )
    op.create_table("stocktransaction",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("tx_type", stock_tx_type, nullable=False),
        sa.Column("quantity", sa.Numeric(12,3), nullable=False),
        sa.Column("unit", sa.String(20), server_default="kg"),
        sa.Column("meta", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )

    # Finance
    op.create_table("account",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("type", sa.Enum(name="acct_type", create_type=False), nullable=False)
    )
    op.create_table("ledgerentry",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("amount", sa.Numeric(14,2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="NGN"),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("meta", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )

    # Audit
    op.create_table("auditlog",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action", sa.String(120), index=True),
        sa.Column("entity", sa.String(120)),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("details", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), nullable=False)
    )

    # --- RLS policies ---
    for table in ["user","membership","farm","fieldplot","crop","variety",
                  "sensordevice","sensor_readings","item","stocktransaction",
                  "account","ledgerentry","auditlog"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        # Select by tenant
        op.execute(f"""
        CREATE POLICY tenant_isolation_select ON {table}
        FOR SELECT USING (tenant_id = app_current_tenant());
        """)
        # Insert/update/delete must match tenant
        op.execute(f"""
        CREATE POLICY tenant_isolation_write ON {table}
        FOR ALL USING (tenant_id = app_current_tenant())
        WITH CHECK (tenant_id = app_current_tenant());
        """)

def downgrade():
    op.execute("DROP FUNCTION IF EXISTS app_current_tenant()")
    op.drop_table("auditlog")
    op.drop_table("ledgerentry")
    op.drop_table("account")
    op.drop_table("stocktransaction")
    op.drop_table("item")
    op.execute("SELECT drop_chunks(interval '0 days', 'sensor_readings')")
    op.drop_table("sensor_readings")
    op.drop_table("sensordevice")
    op.drop_table("variety")
    op.drop_table("crop")
    op.drop_table("fieldplot")
    op.drop_table("farm")
    op.drop_table("user")
    op.drop_table("membership")
    op.drop_table("tenant")
    op.execute("DROP TYPE IF EXISTS crop_category")
    op.execute("DROP TYPE IF EXISTS stock_tx_type")
    op.execute("DROP TYPE IF EXISTS acct_type")
