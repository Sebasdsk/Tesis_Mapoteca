"""
Authentication Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.models.usuario import TipoUsuarioEnum


# Schema for login request
class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., description="Número de cuenta/empleado o username")
    password: str = Field(..., min_length=1)


# Schema for token response
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Seconds until expiration")
    user: "TokenUser"


# Schema for user info in token response
class TokenUser(BaseModel):
    """Schema for user info included in token response"""
    id: UUID
    tipo_usuario: TipoUsuarioEnum
    nombre_completo: str
    email: Optional[str]
    debe_cambiar_password: bool
    
    class Config:
        from_attributes = True


# Schema for token payload
class TokenPayload(BaseModel):
    """Schema for JWT token payload"""
    sub: UUID  # user_id
    exp: int  # expiration timestamp
