"""
Security utilities: JWT tokens and password hashing
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def _create_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    """
    Create a signed JWT with a type claim.

    Args:
        data: Claims to encode (normalmente {"sub": user_id})
        token_type: "access" o "refresh"
        expires_delta: Tiempo de vida del token
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update({
        "exp": now + expires_delta,
        "iat": now,
        "type": token_type,
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a short-lived JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, "access", expires_delta)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> Tuple[str, str, datetime]:
    """
    Create a long-lived refresh token.

    Returns:
        (token, jti, expires_at)
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    jti = secrets.token_urlsafe(32)
    to_encode.update({
        "exp": now + expires_delta,
        "iat": now,
        "type": "refresh",
        "jti": jti,
    })
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, now + expires_delta


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Returns:
        Decoded payload or None if invalid
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# Alias retrocompatible
decode_access_token = decode_token


def generate_temp_password(length: int = 8) -> str:
    """
    Generate a cryptographically secure random temporary password.

    Usa el modulo `secrets` (no `random`) para evitar contraseñas predecibles.
    """
    import string

    characters = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(characters) for _ in range(length))
        if (any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)):
            return password
