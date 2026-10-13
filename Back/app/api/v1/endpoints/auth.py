"""
Authentication endpoints - CU-01: Inicio de Sesión
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.dependencies import get_db, get_current_user
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
)
from app.core.config import settings
from app.core.limiter import limiter
from app.models.usuario import Usuario
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest, Token, TokenUser
from app.schemas.usuario import PasswordChange


router = APIRouter()


# --- Helpers de cookie/refresh ---

def _set_refresh_cookie(response: Response, token: str) -> None:
    """Set the httpOnly refresh cookie"""
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")


def _issue_session(db: Session, user: Usuario) -> tuple[Token, str]:
    """
    Emite un access token (respuesta) y un refresh token (cookie) para el
    usuario, persistiendo el refresh para poder revocarlo/rotarlo.

    Returns:
        (Token de respuesta, refresh_token en claro para la cookie)
    """
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token, jti, expires_at = create_refresh_token(data={"sub": str(user.id)})

    db.add(RefreshToken(jti=jti, usuario_id=user.id, expires_at=expires_at))
    db.commit()

    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=TokenUser.model_validate(user),
    )
    return token, refresh_token


def _revoke_from_cookie(request: Request, db: Session) -> None:
    """Revoca el refresh token presente en la cookie (si es válido)."""
    raw = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw:
        return
    payload = decode_token(raw)
    if not payload:
        return
    row = db.query(RefreshToken).filter(RefreshToken.jti == payload.get("jti")).first()
    if row and not row.revoked:
        row.revoked = True
        db.commit()


# --- Endpoints ---

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    CU-01: Inicio de Sesión

    Authenticate user and return a short-lived JWT access token.
    Sets a long-lived refresh token in an httpOnly cookie.
    Username can be numero_identificacion or admin username.
    """
    user = db.query(Usuario).filter(
        (Usuario.numero_identificacion == login_data.username) |
        ((Usuario.tipo_usuario == "ADMIN") & (Usuario.nombre_completo == login_data.username))
    ).first()

    if not user or not user.password_hash or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Número de cuenta o contraseña incorrectos"
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )

    token, refresh_token = _issue_session(db, user)
    _set_refresh_cookie(response, refresh_token)
    return token


@router.post("/refresh", response_model=Token)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Rota el refresh token de la cookie y emite un nuevo access token.
    Revoca el refresh anterior (rotación) para detectar reuso.
    """
    raw = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida")

    payload = decode_token(raw)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida")

    row = db.query(RefreshToken).filter(RefreshToken.jti == payload.get("jti")).first()
    if not row or row.revoked or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión expirada")

    user = db.query(Usuario).filter(Usuario.id == row.usuario_id).first()
    if not user or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no válido")

    # Rotación: revocar el anterior y emitir uno nuevo
    row.revoked = True
    token, refresh_token = _issue_session(db, user)
    _set_refresh_cookie(response, refresh_token)
    return token


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Revoca el refresh token y limpia la cookie de sesión."""
    _revoke_from_cookie(request, db)
    _clear_refresh_cookie(response)
    return {"message": "Sesión cerrada correctamente"}


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
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

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
    return TokenUser.model_validate(current_user)
