from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ReporteGeneral(BaseModel):
    total_usuarios: int
    total_cartas: int
    prestamos_activos: int
    consultas_totales: int

class CartaEstadistica(BaseModel):
    carta_id: UUID
    nomenclatura: str
    nombre: str
    escala: str
    cantidad: int

class PrestamoVencido(BaseModel):
    prestamo_id: UUID
    usuario_nombre: str
    usuario_email: Optional[str]
    carta_nomenclatura: str
    carta_nombre: str
    fecha_solicitud: datetime
    fecha_limite: datetime
    dias_retraso: int


class PrestamoActivo(BaseModel):
    prestamo_id: UUID
    usuario_nombre: str
    usuario_email: Optional[str]
    usuario_telefono: Optional[str]
    usuario_identificacion: Optional[str]
    carta_nomenclatura: str
    carta_nombre: str
    fecha_entrega: Optional[datetime]
    fecha_limite: Optional[datetime]
    dias_retraso: int

class DistribucionUsuarios(BaseModel):
    tipo_usuario: str
    cantidad: int

class ActividadMensual(BaseModel):
    mes: str  # format: "2026-01"
    cantidad: int

