"""
ConsultaCatalogo model - tracks searching and viewing maps for statistics
CU-07: Consultar Catálogo (Auditoría y Estadísticas)
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class ConsultaCatalogo(Base):
    """
    Tracks every time a user performs a search or views a specific map.
    This data will be used to generate the 'Most Popular Maps' reports.
    """
    __tablename__ = "consultas_catalogo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who did the query
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # If it was a specific map view
    carta_id = Column(UUID(as_uuid=True), ForeignKey("cartas.id"), nullable=True)
    
    # Search metadata
    termino_busqueda = Column(String(255), nullable=True)
    filtros = Column(JSONB, nullable=True, comment="JSON with applied filters: {tipo, escala, etc}")
    
    # Timestamp
    fecha_consulta = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    usuario = relationship("Usuario", backref="consultas")
    carta = relationship("Carta", backref="consultas")

    def __repr__(self):
        return f"<ConsultaCatalogo {self.id} - User:{self.usuario_id}>"
