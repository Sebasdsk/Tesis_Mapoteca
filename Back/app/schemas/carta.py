"""
Carta Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, ConfigDict, Field, validator, field_validator
from typing import Optional, Dict, Any, Literal
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from app.models.carta import TipoCartaEnum, DisponibilidadEnum, TipoCoordenadasEnum
from app.models.fuente_inegi import EstadoEnlaceEnum
from app.services.inegi import validar_url_inegi
from app.services.coordenadas import parse_coordenada


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
    proyeccion_cartografica: Optional[str] = Field(None, max_length=100)
    coordenadas_utm_x: Optional[str] = Field(None, max_length=50)
    coordenadas_utm_y: Optional[str] = Field(None, max_length=50)
    coordenadas_latitud: Optional[str] = Field(None, max_length=50)
    coordenadas_longitud: Optional[str] = Field(None, max_length=50)
    limites_detalle: Optional[str] = Field(None, max_length=255)
    limites_norte: Optional[Decimal] = None
    limites_sur: Optional[Decimal] = None
    limites_este: Optional[Decimal] = None
    limites_oeste: Optional[Decimal] = None
    anio_edicion: Optional[int] = Field(None, ge=1500, le=2100, description="Año de edición si solo se conoce el año")
    fecha_edicion: Optional[date] = None
    estado_republica: Optional[str] = Field(None, max_length=100)
    disponibilidad: DisponibilidadEnum = DisponibilidadEnum.FISICA
    unidades_total: int = Field(1, ge=1, le=999, description="Número total de copias físicas")
    url_inegi: Optional[str] = None
    metadata_inegi: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata INEGI: {año_digital, formatos_disponibles, escala_digital, fecha_actualizacion}"
    )
    notas: Optional[str] = None


# Schema for creating a new carta
class CartaCreate(CartaBase):
    """Schema for creating a new carta"""

    @field_validator('url_inegi')
    @classmethod
    def validar_referencia(cls, valor):
        if valor is None or not valor.strip():
            return None
        return validar_url_inegi(valor)

    @field_validator('coordenadas_latitud')
    @classmethod
    def validar_latitud(cls, valor):
        if valor is None or not valor.strip():
            return None
        if parse_coordenada(valor, es_longitud=False) is None:
            raise ValueError('Latitud no válida. Use 25.25 o 25°15\'30"N.')
        return valor

    @field_validator('coordenadas_longitud')
    @classmethod
    def validar_longitud(cls, valor):
        if valor is None or not valor.strip():
            return None
        if parse_coordenada(valor, es_longitud=True) is None:
            raise ValueError('Longitud no válida. Use -109.5 o 109°00\'W.')
        return valor
    
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
    proyeccion_cartografica: Optional[str] = Field(None, max_length=100)
    coordenadas_utm_x: Optional[str] = Field(None, max_length=50)
    coordenadas_utm_y: Optional[str] = Field(None, max_length=50)
    coordenadas_latitud: Optional[str] = Field(None, max_length=50)
    coordenadas_longitud: Optional[str] = Field(None, max_length=50)
    limites_detalle: Optional[str] = Field(None, max_length=255)
    limites_norte: Optional[Decimal] = None
    limites_sur: Optional[Decimal] = None
    limites_este: Optional[Decimal] = None
    limites_oeste: Optional[Decimal] = None
    anio_edicion: Optional[int] = Field(None, ge=1500, le=2100)
    fecha_edicion: Optional[date] = None
    estado_republica: Optional[str] = Field(None, max_length=100)
    disponibilidad: Optional[DisponibilidadEnum] = None
    unidades_total: Optional[int] = Field(None, ge=1, le=999)
    url_inegi: Optional[str] = None
    metadata_inegi: Optional[Dict[str, Any]] = None
    notas: Optional[str] = None

    @field_validator('url_inegi')
    @classmethod
    def validar_referencia(cls, valor):
        if valor is None or not valor.strip():
            return None
        return validar_url_inegi(valor)

    @field_validator('coordenadas_latitud')
    @classmethod
    def validar_latitud(cls, valor):
        if valor is None or not valor.strip():
            return None
        if parse_coordenada(valor, es_longitud=False) is None:
            raise ValueError('Latitud no válida. Use 25.25 o 25°15\'30"N.')
        return valor

    @field_validator('coordenadas_longitud')
    @classmethod
    def validar_longitud(cls, valor):
        if valor is None or not valor.strip():
            return None
        if parse_coordenada(valor, es_longitud=True) is None:
            raise ValueError('Longitud no válida. Use -109.5 o 109°00\'W.')
        return valor


# Schema for response (reading a carta)
class CartaRead(CartaBase):
    """Schema for reading carta data (response)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Referencia oficial del INEGI resuelta para la ficha técnica
class ReferenciaInegiRead(BaseModel):
    """Referencia resuelta: URL específica de la carta o del catálogo oficial"""
    url: str
    nombre: Optional[str] = None
    origen: Literal["carta", "catalogo"]
    estado: Optional[EstadoEnlaceEnum] = None


# Schema para la ficha técnica (incluye la referencia INEGI resuelta)
class CartaDetalle(CartaRead):
    """Carta con la referencia INEGI resuelta (CU-12)"""
    referencia_inegi: Optional[ReferenciaInegiRead] = None
    unidades_prestadas: int = 0
    unidades_disponibles: int = 0


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
    unidades_total: int

    model_config = ConfigDict(from_attributes=True)


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


# Schemas para carga masiva (CU-04)
class CargaMasivaResultRow(BaseModel):
    """Resultado de una fila procesada en la carga masiva"""
    fila: int
    nomenclatura: str
    nombre: str
    exito: bool
    mensaje: str

class CargaMasivaResult(BaseModel):
    """Resultado general de la carga masiva"""
    total_procesadas: int
    exitosas: int
    errores: int
    detalle: list[CargaMasivaResultRow]
