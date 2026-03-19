"""
Usuario Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.usuario import TipoUsuarioEnum


# Base schema with common fields
class UsuarioBase(BaseModel):
    """Base schema with common user fields"""
    tipo_usuario: TipoUsuarioEnum
    numero_identificacion: Optional[str] = Field(None, max_length=50)
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    institucion: Optional[str] = Field(None, max_length=255)


# Schema for creating a new user
class UsuarioCreate(UsuarioBase):
    """Schema for creating a new user (admin only)"""
    
    @validator('numero_identificacion')
    def validate_numero_identificacion(cls, v, values):
        """Validate that numero_identificacion is required for non-EXTERNO users"""
        tipo = values.get('tipo_usuario')
        if tipo and tipo != TipoUsuarioEnum.EXTERNO and not v:
            raise ValueError('numero_identificacion es obligatorio para estudiantes, maestros y admins')
        return v
    
    @validator('institucion')
    def validate_institucion(cls, v, values):
        """Validate that institucion is only for EXTERNO users"""
        tipo = values.get('tipo_usuario')
        if v and tipo != TipoUsuarioEnum.EXTERNO:
            raise ValueError('institucion solo aplica para usuarios externos')
        return v


# Schema for updating a user
class UsuarioUpdate(BaseModel):
    """Schema for updating an existing user"""
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None
    institucion: Optional[str] = Field(None, max_length=255)


# Schema for response (reading a user)
class UsuarioRead(UsuarioBase):
    """Schema for reading user data (response)"""
    id: UUID
    activo: bool
    debe_cambiar_password: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for user with password (only shown once after creation)
class UsuarioCreateResponse(UsuarioRead):
    """Schema for response after creating a user (includes temp password)"""
    password_temporal: str = Field(..., description="Contraseña temporal (mostrar solo una vez)")


# Schema for password change
class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that new password and confirmation match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


# Schema for reset password (admin only)
class PasswordReset(BaseModel):
    """Schema for admin resetting a user's password"""
    usuario_id: UUID


# Schema for reset password response
class PasswordResetResponse(BaseModel):
    """Schema for response after resetting password"""
    message: str
    password_temporal: str
