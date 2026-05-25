"""Alembic migration script template."""
"""update estado pago enum

Revision ID: 48b5fdfb9a65
Revises: 6303acc11909
Create Date: 2026-05-24 19:04:34.440164
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '48b5fdfb9a65'
down_revision = '6303acc11909'
branch_labels = None
depends_on = None


def upgrade():

    op.execute(
        "ALTER TYPE estadopagoenum RENAME VALUE 'APROBADO' TO 'PAGADO';"
    )


def downgrade():

    op.execute(
        "ALTER TYPE estadopagoenum RENAME VALUE 'PAGADO' TO 'APROBADO';"
    )