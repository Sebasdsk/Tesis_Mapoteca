"""Add coordinate and projection fields to cartas

Revision ID: add_coord_fields
Revises: 094eae8d4af4
Create Date: 2026-05-28 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_coord_fields'
down_revision: Union[str, None] = '094eae8d4af4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to tipo_coordenadas_enum
    # PG 12+ permite ADD VALUE dentro de una transacción mientras el valor
    # no se use en ella; aquí solo se agregan. IF NOT EXISTS lo hace idempotente.
    # NO usar op.execute("COMMIT") + try/except: un statement fallido aborta
    # la transacción y los siguientes fallan en cascada.
    for val in ['LIMITES', 'UTM', 'AMBAS']:
        op.execute(f"ALTER TYPE tipo_coordenadas_enum ADD VALUE IF NOT EXISTS '{val}'")

    # Add columns to cartas table
    op.add_column('cartas', sa.Column('proyeccion_cartografica', sa.String(length=100), nullable=True))
    op.add_column('cartas', sa.Column('coordenadas_utm_x', sa.String(length=50), nullable=True))
    op.add_column('cartas', sa.Column('coordenadas_utm_y', sa.String(length=50), nullable=True))
    op.add_column('cartas', sa.Column('coordenadas_latitud', sa.String(length=50), nullable=True))
    op.add_column('cartas', sa.Column('coordenadas_longitud', sa.String(length=50), nullable=True))
    op.add_column('cartas', sa.Column('limites_detalle', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Drop columns
    op.drop_column('cartas', 'limites_detalle')
    op.drop_column('cartas', 'coordenadas_longitud')
    op.drop_column('cartas', 'coordenadas_latitud')
    op.drop_column('cartas', 'coordenadas_utm_y')
    op.drop_column('cartas', 'coordenadas_utm_x')
    op.drop_column('cartas', 'proyeccion_cartografica')
