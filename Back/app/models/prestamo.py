"""
Prestamo model - Loan management for the mapoteca
CU-08: Solicitar Préstamo
CU-09: Registrar Préstamo (Entrega)
CU-10: Registrar Devolución y Evaluación
"""
from sqlalchemy import Column, String, Date, DateTime, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base


class EstadoPrestamoEnum(str, enum.Enum):
    """Loan status enumeration"""
    SOLICITADO = "SOLICITADO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ENTREGADO = "ENTREGADO"
    DEVUELTO = "DEVUELTO"
    VENCIDO = "VENCIDO"


class EvaluacionEstadoEnum(str, enum.Enum):
    """Physical condition evaluation at return"""
    BUENO = "BUENO"
    REGULAR = "REGULAR"
    MALO = "MALO"


class Prestamo(Base):
    """
    Préstamo model — tracks the full lifecycle of a map loan:
    Solicitud → Aprobación → Entrega → Devolución + Evaluación
    """
    __tablename__ = "prestamos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    carta_id = Column(UUID(as_uuid=True), ForeignKey("cartas.id"), nullable=False)

    # Estado del préstamo
    estado = Column(
        SQLEnum(EstadoPrestamoEnum),
        nullable=False,
        default=EstadoPrestamoEnum.SOLICITADO
    )

    # Fechas del ciclo de vida
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_aprobacion = Column(DateTime(timezone=True), nullable=True)
    fecha_entrega = Column(DateTime(timezone=True), nullable=True)
    fecha_devolucion = Column(DateTime(timezone=True), nullable=True)
    fecha_limite = Column(Date, nullable=True)

    # Evaluación al devolver (CU-10)
    evaluacion_estado = Column(SQLEnum(EvaluacionEstadoEnum), nullable=True)
    evaluacion_notas = Column(Text, nullable=True)

    # Notas generales
    notas_solicitud = Column(Text, nullable=True)
    notas_admin = Column(Text, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (lazy loaded)
    usuario = relationship("Usuario", backref="prestamos", lazy="joined")
    carta = relationship("Carta", backref="prestamos", lazy="joined")

    def __repr__(self):
        return f"<Prestamo {self.id} - {self.estado}>"
