"""
Prestamo Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from app.models.prestamo import EstadoPrestamoEnum, EvaluacionEstadoEnum


# --- Schemas de Request ---

class PrestamoSolicitar(BaseModel):
    """CU-08: Solicitar préstamo"""
    carta_id: UUID
    notas_solicitud: Optional[str] = Field(None, max_length=500)


class PrestamoAprobar(BaseModel):
    """CU-09: Aprobar solicitud"""
    fecha_limite: date = Field(..., description="Fecha límite de devolución")
    notas_admin: Optional[str] = Field(None, max_length=500)


class PrestamoRechazar(BaseModel):
    """CU-09: Rechazar solicitud"""
    motivo_rechazo: str = Field(..., min_length=1, max_length=500)


class PrestamoEntregar(BaseModel):
    """CU-09: Registrar entrega física"""
    notas_admin: Optional[str] = Field(None, max_length=500)


class PrestamoDevolver(BaseModel):
    """CU-10: Registrar devolución + evaluación"""
    evaluacion_estado: EvaluacionEstadoEnum = Field(..., description="Estado físico: BUENO, REGULAR, MALO")
    evaluacion_notas: Optional[str] = Field(None, max_length=500,
                                            description="Notas sobre el estado físico")


# --- Schemas de Response ---

class CartaEnPrestamo(BaseModel):
    """Carta simplificada para respuestas de préstamo"""
    id: UUID
    nomenclatura: str
    nombre: str
    escala: str

    class Config:
        from_attributes = True


class UsuarioEnPrestamo(BaseModel):
    """Usuario simplificado para respuestas de préstamo"""
    id: UUID
    nombre_completo: str
    tipo_usuario: str
    numero_identificacion: Optional[str]

    class Config:
        from_attributes = True


class PrestamoRead(BaseModel):
    """Schema completo de respuesta"""
    id: UUID
    estado: EstadoPrestamoEnum
    fecha_solicitud: datetime
    fecha_aprobacion: Optional[datetime]
    fecha_entrega: Optional[datetime]
    fecha_devolucion: Optional[datetime]
    fecha_limite: Optional[date]
    evaluacion_estado: Optional[EvaluacionEstadoEnum]
    evaluacion_notas: Optional[str]
    notas_solicitud: Optional[str]
    notas_admin: Optional[str]
    motivo_rechazo: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Relaciones embebidas
    usuario: UsuarioEnPrestamo
    carta: CartaEnPrestamo

    class Config:
        from_attributes = True
