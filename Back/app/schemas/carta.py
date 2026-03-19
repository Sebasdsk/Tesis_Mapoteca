"""
Carta Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from app.models.carta import TipoCartaEnum, DisponibilidadEnum, TipoCoordenadasEnum


# Base schema with common fields
class CartaBase(BaseModel):
    """Base schema with common carta fields"""
    nomenclatura: str = Field(..., max_length=100, description="Clave INEGI única")
    nombre: str = Field(..., min_length=1, max_length=255)
    escala: str = Field(..., max_length=50, description="Ej: 1:50,000")
    tipo_carta: TipoCartaEnum
    elipsoide: Optional[str] = Field(None, max_length=100)
    zona_utm: Optional[str] = Field(None, max_length=10)
    tipo_coordenadas: Optional[TipoCoordenadasEnum] = None
    limites_norte: Optional[Decimal] = None
    limites_sur: Optional[Decimal] = None
    limites_este: Optional[Decimal] = None
    limites_oeste: Optional[Decimal] = None
    fecha_edicion: Optional[date] = None
    estado_republica: Optional[str] = Field(None, max_length=100)
    disponibilidad: DisponibilidadEnum = DisponibilidadEnum.FISICA
    url_inegi: Optional[str] = None
    metadata_inegi: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata INEGI: {año_digital, formatos_disponibles, escala_digital, fecha_actualizacion}"
    )
    notas: Optional[str] = None


# Schema for creating a new carta
class CartaCreate(CartaBase):
    """Schema for creating a new carta"""
    
    @validator('nomenclatura')
    def nomenclatura_uppercase(cls, v):
        """Convert nomenclatura to uppercase"""
        return v.upper().strip() if v else v
    
    @validator('escala')
    def validate_escala(cls, v):
        """Validate escala format"""
        if v and not v.startswith('1:'):
            raise ValueError('La escala debe tener el formato 1:XXXXX (ej: 1:50,000)')
        return v


# Schema for updating a carta
class CartaUpdate(BaseModel):
    """Schema for updating an existing carta"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    escala: Optional[str] = Field(None, max_length=50)
    tipo_carta: Optional[TipoCartaEnum] = None
    elipsoide: Optional[str] = Field(None, max_length=100)
    zona_utm: Optional[str] = Field(None, max_length=10)
    tipo_coordenadas: Optional[TipoCoordenadasEnum] = None
    limites_norte: Optional[Decimal] = None
    limites_sur: Optional[Decimal] = None
    limites_este: Optional[Decimal] = None
    limites_oeste: Optional[Decimal] = None
    fecha_edicion: Optional[date] = None
    estado_republica: Optional[str] = Field(None, max_length=100)
    disponibilidad: Optional[DisponibilidadEnum] = None
    url_inegi: Optional[str] = None
    metadata_inegi: Optional[Dict[str, Any]] = None
    notas: Optional[str] = None


# Schema for response (reading a carta)
class CartaRead(CartaBase):
    """Schema for reading carta data (response)"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for lista simple (usado en búsquedas)
class CartaSimple(BaseModel):
    """Simplified carta schema for lists"""
    id: UUID
    nomenclatura: str
    nombre: str
    escala: str
    tipo_carta: TipoCartaEnum
    estado_republica: Optional[str]
    disponibilidad: DisponibilidadEnum
    
    class Config:
        from_attributes = True


# Schema for baja de carta
class CartaBaja(BaseModel):
    """Schema for giving a carta baja (low)"""
    motivo: str = Field(..., description="PERDIDA, DETERIORO_IRREPARABLE, OBSOLESCENCIA, OTRO")
    descripcion: Optional[str] = Field(None, max_length=500)
    
    @validator('motivo')
    def validate_motivo(cls, v):
        """Validate motivo is one of the allowed values"""
        allowed = ['PERDIDA', 'DETERIORO_IRREPARABLE', 'OBSOLESCENCIA', 'OTRO']
        if v.upper() not in allowed:
            raise ValueError(f'Motivo debe ser uno de: {", ".join(allowed)}')
        return v.upper()
