from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "0004_create_finance_tables"
down_revision = "0003_create_sensors"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('finance_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('amount', sa.Numeric(14,2), nullable=False),
        sa.Column('currency', sa.String(8), server_default='NGN'),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('description', sa.String(400)),
        sa.Column('meta', postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )

    op.create_table('investments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('amount', sa.Numeric(14,2), nullable=False),
        sa.Column('currency', sa.String(8), server_default='NGN'),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('meta', postgresql.JSONB, server_default=sa.text("'{}'::jsonb"))
    )

    op.create_table('payouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('investment_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('amount', sa.Numeric(14,2), nullable=False),
        sa.Column('currency', sa.String(8), server_default='NGN'),
        sa.Column('ts', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('note', sa.String(400))
    )

    op.create_table('receipts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('investment_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('filename', sa.String(255)),
        sa.Column('content', sa.LargeBinary)
    )

    for table in ['finance_transactions','investments','payouts','receipts']:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
        CREATE POLICY tenant_isolation_select ON {table}
        FOR SELECT USING (tenant_id = app_current_tenant());
        """)
        op.execute(f"""
        CREATE POLICY tenant_isolation_write ON {table}
        FOR ALL USING (tenant_id = app_current_tenant())
        WITH CHECK (tenant_id = app_current_tenant());
        """)

def downgrade():
    for table in ['receipts','payouts','investments','finance_transactions']:
        op.drop_table(table)
