from alembic import op
import sqlalchemy as sa
from geoalchemy2.types import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0001_init_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create extensions
    op.execute("""
    DO $$
    BEGIN
        BEGIN
            CREATE EXTENSION IF NOT EXISTS postgis;
        EXCEPTION WHEN OTHERS THEN
            -- ignore
            NULL;
        END;
        BEGIN
            CREATE EXTENSION IF NOT EXISTS timescaledb;
        EXCEPTION WHEN OTHERS THEN
            -- ignore
            NULL;
        END;
        BEGIN
            CREATE EXTENSION IF NOT EXISTS pgcrypto;
        EXCEPTION WHEN OTHERS THEN
            -- ignore
            NULL;
        END;
    END;
    $$;
    """)

    # Helper: tenant_id GUC (used by RLS policies)
    op.execute("""
    CREATE OR REPLACE FUNCTION app_current_tenant() 
    RETURNS uuid 
    AS $$
        SELECT nullif(current_setting('app.tenant_id', true), '')::uuid;
    $$ LANGUAGE SQL STABLE;
    """)
