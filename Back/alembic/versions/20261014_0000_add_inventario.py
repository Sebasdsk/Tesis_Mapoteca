"""Add inventory (unidades_total) and usuario telefono

Revision ID: add_inventario
Revises: add_fuentes_inegi
Create Date: 2026-10-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_inventario'
down_revision: Union[str, None] = 'add_fuentes_inegi'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cartas', sa.Column('unidades_total', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('usuarios', sa.Column('telefono', sa.String(length=30), nullable=True))


def downgrade() -> None:
    op.drop_column('usuarios', 'telefono')
    op.drop_column('cartas', 'unidades_total')
