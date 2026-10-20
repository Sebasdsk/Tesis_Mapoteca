"""Add fuentes_inegi table

Revision ID: add_fuentes_inegi
Revises: add_prestamos_table
Create Date: 2026-10-13 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

# revision identifiers, used by Alembic.
revision: str = 'add_fuentes_inegi'
down_revision: Union[str, None] = 'add_prestamos_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Idempotente por si ya existe (p. ej. creada por create_all).
    if 'fuentes_inegi' in sa.inspect(bind).get_table_names():
        return

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estadoenlaceenum AS ENUM ('sin_verificar','valido','no_responde');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)

    estado_enlace = ENUM(
        'sin_verificar', 'valido', 'no_responde',
        name='estadoenlaceenum', create_type=False,
    )
    tipo_carta = ENUM(
        'TOPOGRAFICA', 'GEOLOGICA', 'HIDROLOGICA', 'EDAFOLOGICA',
        'USO_SUELO', 'CLIMATICA', 'OTRA',
        name='tipo_carta_enum', create_type=False,
    )

    op.create_table(
        'fuentes_inegi',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('escala', sa.String(length=50), nullable=False),
        sa.Column('tipo_carta', tipo_carta, nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('estado_enlace', estado_enlace, nullable=False, server_default='sin_verificar'),
        sa.Column('fecha_verificacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('escala', 'tipo_carta', name='uq_fuentes_inegi_escala_tipo'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_fuentes_inegi_escala', 'fuentes_inegi', ['escala'])
    op.create_index('idx_fuentes_inegi_tipo', 'fuentes_inegi', ['tipo_carta'])


def downgrade() -> None:
    op.drop_index('idx_fuentes_inegi_tipo', 'fuentes_inegi')
    op.drop_index('idx_fuentes_inegi_escala', 'fuentes_inegi')
    op.drop_table('fuentes_inegi')
    op.execute('DROP TYPE IF EXISTS estadoenlaceenum')
