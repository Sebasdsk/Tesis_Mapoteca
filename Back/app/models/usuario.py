"""
Usuario model - represents system users (students, teachers, admins, external)
"""
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class TipoUsuarioEnum(str, enum.Enum):
    """User type enumeration"""
    ADMIN = "ADMIN"
    ESTUDIANTE = "ESTUDIANTE"
    MAESTRO = "MAESTRO"
    EXTERNO = "EXTERNO"


class Usuario(Base):
    """
    Usuario model
    
    Represents all types of users in the system:
    - ADMIN: System administrator
    - ESTUDIANTE: Student users
    - MAESTRO: Teacher/Professor users
    - EXTERNO: External users
    """
    __tablename__ = "usuarios"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User type and identification
    tipo_usuario = Column(SQLEnum(TipoUsuarioEnum), nullable=False, index=True)
    numero_identificacion = Column(
        String(50), 
        unique=True, 
        nullable=True,  # NULL for EXTERNO
        index=True,
        comment="Número de cuenta (estudiante) o empleado (maestro/admin)"
    )
    
    # Personal information
    nombre_completo = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)  # NULL for EXTERNO
    debe_cambiar_password = Column(Boolean, default=True, nullable=False)
    
    # Status
    activo = Column(Boolean, default=True, nullable=False, index=True)
    
    # External users only
    institucion = Column(String(255), nullable=True, comment="Solo para usuarios externos")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, tipo={self.tipo_usuario}, nombre={self.nombre_completo})>"
