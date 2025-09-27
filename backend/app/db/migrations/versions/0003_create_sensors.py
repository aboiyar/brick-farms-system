"""create sensors tables

Revision ID: 0003_create_sensors
Revises: 0002_create_plots
Create Date: 2025-09-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_create_sensors'
down_revision = '0002_create_plots'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    op.execute("""
    CREATE TABLE IF NOT EXISTS sensor_devices (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id uuid NOT NULL,
        farm_id uuid NOT NULL,
        plot_id uuid,
        name varchar(120) NOT NULL,
        protocol varchar(20),
        api_key varchar(64) NOT NULL,
        location geometry(POINT,4326),
        created_at timestamptz DEFAULT now() NOT NULL
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id bigserial PRIMARY KEY,
        tenant_id uuid NOT NULL,
        device_id uuid NOT NULL,
        metric varchar(64),
        value double precision NOT NULL,
        unit varchar(24),
        timestamp timestamptz NOT NULL,
        location geometry(POINT,4326)
    )
    """)

    op.create_index('ix_sensor_devices_tenant', 'sensor_devices', ['tenant_id'])
    op.create_index('ix_sensor_readings_tenant', 'sensor_readings', ['tenant_id'])
    op.create_index('ix_sensor_readings_device', 'sensor_readings', ['device_id'])


def downgrade():
    op.drop_index('ix_sensor_readings_device', table_name='sensor_readings')
    op.drop_index('ix_sensor_readings_tenant', table_name='sensor_readings')
    op.drop_index('ix_sensor_devices_tenant', table_name='sensor_devices')
    op.execute('DROP TABLE IF EXISTS sensor_readings')
    op.execute('DROP TABLE IF EXISTS sensor_devices')
