"""
User management endpoints - CU-02: Gestión de Usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.dependencies import get_db, get_current_admin_user
from app.core.security import get_password_hash, generate_temp_password
from app.models.usuario import Usuario, TipoUsuarioEnum
from app.schemas.usuario import (
    UsuarioCreate, 
    UsuarioRead, 
    UsuarioUpdate, 
    UsuarioCreateResponse,
    PasswordReset,
    PasswordResetResponse
)


router = APIRouter()


@router.post("/", response_model=UsuarioCreateResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Crear Usuario
    
    Create a new user (admin only).
    Generates a temporary password automatically.
    """
    # Validate unique numero_identificacion
    if usuario_data.numero_identificacion:
        existing = db.query(Usuario).filter(
            Usuario.numero_identificacion == usuario_data.numero_identificacion
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El número de identificación {usuario_data.numero_identificacion} ya está registrado"
            )
    
    # Generate temporary password
    temp_password = generate_temp_password(8)
    
    # Create new user
    new_user = Usuario(
        tipo_usuario=usuario_data.tipo_usuario,
        numero_identificacion=usuario_data.numero_identificacion,
        nombre_completo=usuario_data.nombre_completo,
        email=usuario_data.email,
        institucion=usuario_data.institucion,
        password_hash=get_password_hash(temp_password) if usuario_data.tipo_usuario != TipoUsuarioEnum.EXTERNO else None,
        debe_cambiar_password=True if usuario_data.tipo_usuario != TipoUsuarioEnum.EXTERNO else False,
        activo=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return user with temporary password
    response = UsuarioCreateResponse.from_orm(new_user)
    response.password_temporal = temp_password
    
    return response


@router.get("/", response_model=List[UsuarioRead])
def list_usuarios(
    skip: int = 0,
    limit: int = 100,
    tipo_usuario: TipoUsuarioEnum = None,
    activo: bool = None,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Listar Usuarios
    
    List all users with optional filters (admin only).
    """
    query = db.query(Usuario)
    
    # Apply filters
    if tipo_usuario:
        query = query.filter(Usuario.tipo_usuario == tipo_usuario)
    
    if activo is not None:
        query = query.filter(Usuario.activo == activo)
    
    # Order by creation date (newest first)
    query = query.order_by(Usuario.created_at.desc())
    
    # Pagination
    usuarios = query.offset(skip).limit(limit).all()
    
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioRead)
def get_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Obtener Usuario por ID
    
    Get a specific user by ID (admin only).
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRead)
def update_usuario(
    usuario_id: UUID,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Actualizar Usuario
    
    Update an existing user (admin only).
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Update fields
    update_data = usuario_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


@router.delete("/{usuario_id}")
def deactivate_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Desactivar Usuario (Soft Delete)
    
    Deactivate a user instead of deleting (preserves history).
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Prevent self-deactivation
    if usuario.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    # Soft delete
    usuario.activo = False
    db.commit()
    
    return {
        "message": "Usuario desactivado correctamente",
        "usuario_id": str(usuario.id),
        "nombre": usuario.nombre_completo
    }


@router.post("/{usuario_id}/activate")
def activate_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Reactivar Usuario
    
    Reactivate a previously deactivated user.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    usuario.activo = True
    db.commit()
    
    return {
        "message": "Usuario reactivado correctamente",
        "usuario_id": str(usuario.id),
        "nombre": usuario.nombre_completo
    }


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_user_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin_user)
):
    """
    CU-02: Resetear Contraseña de Usuario
    
    Reset a user's password to a new temporary password (admin only).
    """
    usuario = db.query(Usuario).filter(Usuario.id == reset_data.usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if usuario.tipo_usuario == TipoUsuarioEnum.EXTERNO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los usuarios externos no tienen contraseña"
        )
    
    # Generate new temporary password
    temp_password = generate_temp_password(8)
    
    # Update password
    usuario.password_hash = get_password_hash(temp_password)
    usuario.debe_cambiar_password = True
    
    db.commit()
    
    return PasswordResetResponse(
        message="Contraseña reseteada correctamente",
        password_temporal=temp_password
    )
