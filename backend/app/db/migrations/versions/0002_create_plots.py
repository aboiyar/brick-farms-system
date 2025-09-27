"""create plots table

Revision ID: 0002_create_plots
Revises: 0001_init_core
Create Date: 2025-09-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_create_plots'
down_revision = '0001_init_core'
branch_labels = None
depends_on = None


def upgrade():
    # ensure PostGIS
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    op.execute("""
    CREATE TABLE IF NOT EXISTS plots (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id uuid NOT NULL,
        farm_id uuid NOT NULL,
        name varchar(200) NOT NULL,
        description text,
        crop_type varchar(120),
        area_ha double precision,
        geom geometry(POLYGON,4326) NOT NULL,
        created_at timestamptz DEFAULT now() NOT NULL,
        updated_at timestamptz DEFAULT now() NOT NULL
    )
    """)
    op.create_index('ix_plots_tenant_id', 'plots', ['tenant_id'])
    op.create_index('ix_plots_farm_id', 'plots', ['farm_id'])


def downgrade():
    op.drop_index('ix_plots_farm_id', table_name='plots')
    op.drop_index('ix_plots_tenant_id', table_name='plots')
    op.execute('DROP TABLE IF EXISTS plots')
