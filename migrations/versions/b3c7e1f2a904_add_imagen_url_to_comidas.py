"""add imagenUrl to comidas

Revision ID: b3c7e1f2a904
Revises: 224a40b3e3be
Create Date: 2026-05-25 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'b3c7e1f2a904'
down_revision = '224a40b3e3be'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('comidas', sa.Column('imagenUrl', sa.String(), nullable=True))


def downgrade():
    op.drop_column('comidas', 'imagenUrl')
