"""
Core configuration settings for the Mapoteca System
"""
from pydantic import model_validator
from pydantic_settings import BaseSettings
from typing import List


# Valores conocidos/inseguros que NO deben usarse en producción.
INSECURE_SECRET_KEYS = {
    "dev-secret-key-cambiar-en-produccion",
    "cambia-esto-por-una-clave-segura-en-produccion",
    "changeme",
    "secret",
    "secret-key",
}
INSECURE_ADMIN_PASSWORDS = {"Admin123!"}


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Entorno: "development" | "production"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Refresh cookie
    REFRESH_COOKIE_NAME: str = "mapoteca_refresh"
    # Si es None, se deriva del entorno (Secure en producción).
    COOKIE_SECURE: bool | None = None
    COOKIE_SAMESITE: str = "lax"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:4200"

    # App
    APP_NAME: str = "Sistema de Gestión de Mapoteca UAS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@mapoteca.uas.edu.mx"
    ADMIN_PASSWORD: str = "Admin123!"

    @property
    def is_production(self) -> bool:
        """True si el entorno es producción"""
        return self.ENVIRONMENT.strip().lower() in ("production", "prod")

    @property
    def cors_origins(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def cookie_secure(self) -> bool:
        """Secure en producción salvo que se fuerce explícitamente"""
        if self.COOKIE_SECURE is not None:
            return self.COOKIE_SECURE
        return self.is_production

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """
        Fail-fast: en producción no se permite arrancar con secretos por
        defecto o débiles. Evita desplegar con un SECRET_KEY falsificable.
        """
        if self.is_production:
            if self.SECRET_KEY in INSECURE_SECRET_KEYS or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY insegura para producción. Genera una con: "
                    "python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            if self.ADMIN_PASSWORD in INSECURE_ADMIN_PASSWORDS:
                raise ValueError(
                    "ADMIN_PASSWORD no puede ser la contraseña por defecto en producción."
                )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
