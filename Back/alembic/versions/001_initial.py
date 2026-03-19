"""
Initial database schema

Revision ID: 001_initial
Create Date: 2026-03-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema"""
    
    # Create ENUM types
    op.execute("""
        CREATE TYPE tipo_usuario_enum AS ENUM ('ADMIN', 'ESTUDIANTE', 'MAESTRO', 'EXTERNO');
        CREATE TYPE tipo_carta_enum AS ENUM ('TOPOGRAFICA', 'GEOLOGICA', 'HIDROLOGICA', 'EDAFOLOGICA', 'USO_SUELO', 'CLIMATICA', 'OTRA');
        CREATE TYPE disponibilidad_enum AS ENUM ('FISICA', 'SOLO_DIGITAL', 'AMBAS', 'EXTRAVIADA', 'DANADA');
        CREATE TYPE tipo_coordenadas_enum AS ENUM ('ALTOMETRICO', 'GEODESICO');
    """)
    
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tipo_usuario', sa.Enum('ADMIN', 'ESTUDIANTE', 'MAESTRO', 'EXTERNO', name='tipo_usuario_enum'), nullable=False),
        sa.Column('numero_identificacion', sa.String(50), unique=True, nullable=True),
        sa.Column('nombre_completo', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('debe_cambiar_password', sa.Boolean(), default=True, nullable=False),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('institucion', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for usuarios
    op.create_index('idx_usuarios_tipo', 'usuarios', ['tipo_usuario'])
    op.create_index('idx_usuarios_numero_identificacion', 'usuarios', ['numero_identificacion'])
    op.create_index('idx_usuarios_activo', 'usuarios', ['activo'])
    
    # Create cartas table
    op.create_table(
        'cartas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('nomenclatura', sa.String(100), unique=True, nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('escala', sa.String(50), nullable=False),
        sa.Column('tipo_carta', sa.Enum('TOPOGRAFICA', 'GEOLOGICA', 'HIDROLOGICA', 'EDAFOLOGICA', 'USO_SUELO', 'CLIMATICA', 'OTRA', name='tipo_carta_enum'), nullable=False),
        sa.Column('elipsoide', sa.String(100), nullable=True),
        sa.Column('zona_utm', sa.String(10), nullable=True),
        sa.Column('tipo_coordenadas', sa.Enum('ALTOMETRICO', 'GEODESICO', name='tipo_coordenadas_enum'), nullable=True),
        sa.Column('limites_norte', sa.Numeric(10, 6), nullable=True),
        sa.Column('limites_sur', sa.Numeric(10, 6), nullable=True),
        sa.Column('limites_este', sa.Numeric(10, 6), nullable=True),
        sa.Column('limites_oeste', sa.Numeric(10, 6), nullable=True),
        sa.Column('fecha_edicion', sa.Date(), nullable=True),
        sa.Column('estado_republica', sa.String(100), nullable=True),
        sa.Column('disponibilidad', sa.Enum('FISICA', 'SOLO_DIGITAL', 'AMBAS', 'EXTRAVIADA', 'DANADA', name='disponibilidad_enum'), nullable=False, server_default='FISICA'),
        sa.Column('url_inegi', sa.Text(), nullable=True),
        sa.Column('metadata_inegi', JSONB, nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for cartas
    op.create_index('idx_cartas_nomenclatura', 'cartas', ['nomenclatura'])
    op.create_index('idx_cartas_tipo', 'cartas', ['tipo_carta'])
    op.create_index('idx_cartas_disponibilidad', 'cartas', ['disponibilidad'])
    op.create_index('idx_cartas_estado', 'cartas', ['estado_republica'])
    op.create_index('idx_cartas_escala', 'cartas', ['escala'])


def downgrade() -> None:
    """Drop all tables and types"""
    
    # Drop indexes
    op.drop_index('idx_cartas_escala', 'cartas')
    op.drop_index('idx_cartas_estado', 'cartas')
    op.drop_index('idx_cartas_disponibilidad', 'cartas')
    op.drop_index('idx_cartas_tipo', 'cartas')
    op.drop_index('idx_cartas_nomenclatura', 'cartas')
    
    op.drop_index('idx_usuarios_activo', 'usuarios')
    op.drop_index('idx_usuarios_numero_identificacion', 'usuarios')
    op.drop_index('idx_usuarios_tipo', 'usuarios')
    
    # Drop tables
    op.drop_table('cartas')
    op.drop_table('usuarios')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS tipo_coordenadas_enum')
    op.execute('DROP TYPE IF EXISTS disponibilidad_enum')
    op.execute('DROP TYPE IF EXISTS tipo_carta_enum')
    op.execute('DROP TYPE IF EXISTS tipo_usuario_enum')
