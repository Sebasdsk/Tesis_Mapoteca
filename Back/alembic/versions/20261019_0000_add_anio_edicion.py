"""Add anio_edicion (year-only edition) to cartas

Revision ID: add_anio_edicion
Revises: add_inventario
Create Date: 2026-10-19 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_anio_edicion'
down_revision: Union[str, None] = 'add_inventario'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'cartas',
        sa.Column(
            'anio_edicion',
            sa.Integer(),
            nullable=True,
            comment='Año de edición cuando no se conoce la fecha completa',
        ),
    )
    # Backfill: las cartas con fecha completa ya conocen su año.
    op.execute(
        "UPDATE cartas SET anio_edicion = EXTRACT(YEAR FROM fecha_edicion)::int "
        "WHERE fecha_edicion IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column('cartas', 'anio_edicion')
