"""Add refresh_tokens table

Revision ID: add_refresh_tokens
Revises: add_coord_fields
Create Date: 2026-10-12 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'add_refresh_tokens'
down_revision: Union[str, None] = 'add_coord_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('jti', sa.String(length=64), nullable=False),
        sa.Column('usuario_id', UUID(as_uuid=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_refresh_tokens_jti', 'refresh_tokens', ['jti'], unique=True)
    op.create_index('idx_refresh_tokens_usuario', 'refresh_tokens', ['usuario_id'])


def downgrade() -> None:
    op.drop_index('idx_refresh_tokens_usuario', 'refresh_tokens')
    op.drop_index('idx_refresh_tokens_jti', 'refresh_tokens')
    op.drop_table('refresh_tokens')
