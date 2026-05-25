"""add descripcion to comidas

Revision ID: c4d8f2e1b705
Revises: b3c7e1f2a904
Create Date: 2026-05-25 11:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'c4d8f2e1b705'
down_revision = 'b3c7e1f2a904'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('comidas', sa.Column('descripcion', sa.String(), nullable=True))


def downgrade():
    op.drop_column('comidas', 'descripcion')
