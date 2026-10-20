"""
Schemas de FuenteInegi (catálogo de referencias oficiales del INEGI).
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.carta import TipoCartaEnum
from app.models.fuente_inegi import EstadoEnlaceEnum
from app.services.inegi import validar_url_inegi


class FuenteInegiBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    escala: str = Field(..., min_length=3, max_length=50)
    tipo_carta: TipoCartaEnum
    nombre: str = Field(..., min_length=1, max_length=150)
    url: str = Field(..., min_length=1)

    @field_validator("url")
    @classmethod
    def _validar_dominio(cls, v: str) -> str:
        return validar_url_inegi(v)

    @field_validator("escala")
    @classmethod
    def _validar_escala(cls, v: str) -> str:
        denominador = v.removeprefix("1:").replace(",", "")
        if not v.startswith("1:") or not denominador.isascii() or not denominador.isdigit() or int(denominador) <= 0:
            raise ValueError("La escala debe usar el formato 1:XXXXX (ejemplo: 1:50,000)")
        return v


class FuenteInegiCreate(FuenteInegiBase):
    pass


class FuenteInegiUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    escala: Optional[str] = Field(None, min_length=3, max_length=50)
    tipo_carta: Optional[TipoCartaEnum] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    url: Optional[str] = Field(None, min_length=1)

    @field_validator("url")
    @classmethod
    def _validar_dominio(cls, v: Optional[str]) -> Optional[str]:
        return validar_url_inegi(v) if v is not None else v

    @field_validator("escala")
    @classmethod
    def _validar_escala(cls, v: Optional[str]) -> Optional[str]:
        return FuenteInegiBase._validar_escala(v) if v is not None else v

    @model_validator(mode="after")
    def _rechazar_nulos(self):
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Los campos de la fuente no pueden quedar vacíos")
        return self


class FuenteInegiRead(FuenteInegiBase):
    id: UUID
    estado_enlace: EstadoEnlaceEnum
    fecha_verificacion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
