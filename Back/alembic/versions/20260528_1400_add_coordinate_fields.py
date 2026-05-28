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
    # Add new values to tipocoordenadasenum
    # We execute COMMIT to ensure we are not in a transaction block, as PostgreSQL doesn't allow ALTER TYPE ADD VALUE in a transaction
    op.execute("COMMIT")
    for val in ['LIMITES', 'UTM', 'GEODESICO', 'AMBAS']:
        try:
            op.execute(f"ALTER TYPE tipocoordenadasenum ADD VALUE '{val}'")
        except Exception:
            pass
        try:
            op.execute(f"ALTER TYPE tipo_coordenadas_enum ADD VALUE '{val}'")
        except Exception:
            pass

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
