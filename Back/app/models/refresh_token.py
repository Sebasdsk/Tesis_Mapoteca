"""
RefreshToken model - persistencia de refresh tokens para rotación y revocación.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class RefreshToken(Base):
    """
    Cada fila representa un refresh token emitido. Guardamos el `jti` para
    poder revocarlo (logout) y rotarlo (refresh) sin confiar solo en el JWT.
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = Column(String(64), unique=True, nullable=False, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", backref="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken jti={self.jti} user={self.usuario_id} revoked={self.revoked}>"
