"""
FuenteInegi model - catálogo de referencias oficiales del INEGI.

El administrador no captura un enlace por cada carta: mantiene un catálogo
pequeño de enlaces oficiales por (escala, tipo_carta) y el sistema resuelve
automáticamente la referencia de cada carta.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base
from app.models.carta import TipoCartaEnum


class EstadoEnlaceEnum(str, enum.Enum):
    """Estado de la última verificación del enlace"""
    SIN_VERIFICAR = "sin_verificar"
    VALIDO = "valido"
    NO_RESPONDE = "no_responde"


class FuenteInegi(Base):
    """
    Fuente oficial del INEGI por escala y tipo de carta.
    UNIQUE(escala, tipo_carta): una sola fila por combinación.
    """
    __tablename__ = "fuentes_inegi"
    __table_args__ = (
        UniqueConstraint("escala", "tipo_carta", name="uq_fuentes_inegi_escala_tipo"),
        Index("idx_fuentes_inegi_escala", "escala"),
        Index("idx_fuentes_inegi_tipo", "tipo_carta"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escala = Column(String(50), nullable=False)
    tipo_carta = Column(SQLEnum(TipoCartaEnum, name="tipo_carta_enum"), nullable=False)
    nombre = Column(String(150), nullable=False)
    url = Column(Text, nullable=False)
    estado_enlace = Column(
        SQLEnum(
            EstadoEnlaceEnum,
            name="estadoenlaceenum",
            values_callable=lambda estados: [estado.value for estado in estados],
        ),
        nullable=False,
        default=EstadoEnlaceEnum.SIN_VERIFICAR,
        server_default="sin_verificar",
    )
    fecha_verificacion = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<FuenteInegi {self.escala} {self.tipo_carta} -> {self.url}>"
