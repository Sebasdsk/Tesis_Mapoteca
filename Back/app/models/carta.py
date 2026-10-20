"""
Carta model - represents physical maps in the mapoteca
"""
from sqlalchemy import Column, String, Date, Enum as SQLEnum, Numeric, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class TipoCartaEnum(str, enum.Enum):
    """Map type enumeration"""
    TOPOGRAFICA = "TOPOGRAFICA"
    GEOLOGICA = "GEOLOGICA"
    HIDROLOGICA = "HIDROLOGICA"
    EDAFOLOGICA = "EDAFOLOGICA"
    USO_SUELO = "USO_SUELO"
    CLIMATICA = "CLIMATICA"
    OTRA = "OTRA"


class DisponibilidadEnum(str, enum.Enum):
    """Availability status enumeration"""
    FISICA = "FISICA"  # Available physically in mapoteca
    SOLO_DIGITAL = "SOLO_DIGITAL"  # Only digital reference (INEGI)
    AMBAS = "AMBAS"  # Both physical and digital
    EXTRAVIADA = "EXTRAVIADA"  # Lost
    DANADA = "DANADA"  # Damaged/not loanable


class TipoCoordenadasEnum(str, enum.Enum):
    """Coordinate type enumeration"""
    LIMITES = "LIMITES"
    UTM = "UTM"
    GEODESICO = "GEODESICO"
    AMBAS = "AMBAS"
    ALTOMETRICO = "ALTOMETRICO"


class Carta(Base):
    """
    Carta model
    
    Represents physical maps with all technical metadata required
    for cartographic classification and location.
    """
    __tablename__ = "cartas"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic identification
    nomenclatura = Column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Clave INEGI única (ej: G13-A12)"
    )
    nombre = Column(String(255), nullable=False, comment="Nombre de la carta (ej: Culiacán)")
    escala = Column(String(50), nullable=False, index=True, comment="Ej: 1:50,000")
    tipo_carta = Column(SQLEnum(TipoCartaEnum), nullable=False, index=True)
    
    # Technical metadata
    elipsoide = Column(String(100), nullable=True, comment="Ej: WGS84, GRS80, Clarke 1866")
    zona_utm = Column(String(10), nullable=True, comment="Ej: 12N, 13N")
    tipo_coordenadas = Column(SQLEnum(TipoCoordenadasEnum), nullable=True)
    proyeccion_cartografica = Column(String(100), nullable=True, comment="Ej: Transversa de Mercator")
    
    # New coordinate fields
    coordenadas_utm_x = Column(String(50), nullable=True, comment="Coordenada UTM X (ej: 702,000)")
    coordenadas_utm_y = Column(String(50), nullable=True, comment="Coordenada UTM Y (ej: 2,794,000)")
    coordenadas_latitud = Column(String(50), nullable=True, comment="Latitud geodésica (ej: 25° 15´)")
    coordenadas_longitud = Column(String(50), nullable=True, comment="Longitud geodésica (ej: 109° 00´)")
    limites_detalle = Column(String(255), nullable=True, comment="Detalle de límites (ej: ESTATAL, INTERNACIONAL)")
    
    # Geographic limits (in decimal degrees)
    limites_norte = Column(Numeric(10, 6), nullable=True)
    limites_sur = Column(Numeric(10, 6), nullable=True)
    limites_este = Column(Numeric(10, 6), nullable=True)
    limites_oeste = Column(Numeric(10, 6), nullable=True)
    
    # Date and location
    anio_edicion = Column(Integer, nullable=True, comment="Año de edición cuando no se conoce la fecha completa")
    fecha_edicion = Column(Date, nullable=True, comment="Fecha completa de edición de la carta física")
    estado_republica = Column(String(100), nullable=True, index=True)
    
    # Availability
    disponibilidad = Column(
        SQLEnum(DisponibilidadEnum), 
        nullable=False, 
        default=DisponibilidadEnum.FISICA,
        index=True
    )

    # Inventario: número total de copias físicas
    unidades_total = Column(Integer, nullable=False, default=1, server_default="1")
    
    # INEGI references
    url_inegi = Column(Text, nullable=True, comment="URL directa al archivo en INEGI")
    metadata_inegi = Column(
        JSONB, 
        nullable=True,
        comment="Info adicional: {año_digital, formatos_disponibles, escala_digital, fecha_actualizacion}"
    )
    
    # Notes
    notas = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Carta(id={self.id}, nomenclatura={self.nomenclatura}, nombre={self.nombre})>"
