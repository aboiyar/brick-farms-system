"""create user_preferences table

Revision ID: 0005_create_user_preferences
Revises: 0004_create_finance_tables
Create Date: 2025-09-27
"""
from alembic import op
import sqlalchemy as sa

revision = '0005_create_user_preferences'
down_revision = '0004_create_finance_tables'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.UniqueConstraint('tenant_id', 'user_id', 'key', name='uq_user_pref_key')
    )


def downgrade():
    op.drop_table('user_preferences')
