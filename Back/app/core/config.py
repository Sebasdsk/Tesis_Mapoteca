"""
Core configuration settings for the Mapoteca System
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 4
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:4200"
    
    # App
    APP_NAME: str = "Sistema de Gestión de Mapoteca UAS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@mapoteca.uas.edu.mx"
    ADMIN_PASSWORD: str = "Admin123!"
    
    @property
    def cors_origins(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
