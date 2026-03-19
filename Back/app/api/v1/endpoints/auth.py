"""
Authentication endpoints - CU-01: Inicio de Sesión
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.dependencies import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, Token, TokenUser
from app.schemas.usuario import PasswordChange


router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    CU-01: Inicio de Sesión
    
    Authenticate user and return JWT token.
    Username can be numero_identificacion or admin username.
    """
    # Try to find user by numero_identificacion or check if it's admin
    user = db.query(Usuario).filter(
        (Usuario.numero_identificacion == login_data.username) |
        ((Usuario.tipo_usuario == "ADMIN") & (Usuario.nombre_completo == login_data.username))
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Número de cuenta o contraseña incorrectos"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Número de cuenta o contraseña incorrectos"
        )
    
    # Check if user is active
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )
    
    # Create access token
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,  # Convert to seconds
        user=TokenUser.from_orm(user)
    )


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    CU-01: Cambio de Contraseña
    
    Allow user to change their password.
    Required on first login (debe_cambiar_password = True).
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    # Update password
    from app.core.security import get_password_hash
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.debe_cambiar_password = False
    
    db.commit()
    
    return {
        "message": "Contraseña actualizada correctamente",
        "debe_cambiar_password": False
    }


@router.get("/me", response_model=TokenUser)
def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return TokenUser.from_orm(current_user)
