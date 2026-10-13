"""Add prestamos table

La tabla `prestamos` no quedó registrada en una migración previa (la revision
094eae8d4af4 solo creaba consultas_catalogo); hasta ahora solo existía por el
create_all del seed. Esta migración la formaliza de forma idempotente.

Revision ID: add_prestamos_table
Revises: add_refresh_tokens
Create Date: 2026-10-12 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

# revision identifiers, used by Alembic.
revision: str = 'add_prestamos_table'
down_revision: Union[str, None] = 'add_refresh_tokens'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Idempotente: si la tabla ya existe (creada antes por create_all), no hacer nada.
    if 'prestamos' in sa.inspect(bind).get_table_names():
        return

    # Crear los ENUM types sin fallar si ya existen.
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estadoprestamoenum AS ENUM
                ('SOLICITADO','APROBADO','RECHAZADO','ENTREGADO','DEVUELTO','VENCIDO');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE evaluacionestadoenum AS ENUM ('BUENO','REGULAR','MALO');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)

    estado_enum = ENUM(
        'SOLICITADO', 'APROBADO', 'RECHAZADO', 'ENTREGADO', 'DEVUELTO', 'VENCIDO',
        name='estadoprestamoenum', create_type=False,
    )
    evaluacion_enum = ENUM(
        'BUENO', 'REGULAR', 'MALO',
        name='evaluacionestadoenum', create_type=False,
    )

    op.create_table(
        'prestamos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('usuario_id', UUID(as_uuid=True), nullable=False),
        sa.Column('carta_id', UUID(as_uuid=True), nullable=False),
        sa.Column('estado', estado_enum, nullable=False),
        sa.Column('fecha_solicitud', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('fecha_aprobacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_entrega', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_devolucion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_limite', sa.Date(), nullable=True),
        sa.Column('evaluacion_estado', evaluacion_enum, nullable=True),
        sa.Column('evaluacion_notas', sa.Text(), nullable=True),
        sa.Column('notas_solicitud', sa.Text(), nullable=True),
        sa.Column('notas_admin', sa.Text(), nullable=True),
        sa.Column('motivo_rechazo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['carta_id'], ['cartas.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('prestamos')
    op.execute('DROP TYPE IF EXISTS evaluacionestadoenum')
    op.execute('DROP TYPE IF EXISTS estadoprestamoenum')
