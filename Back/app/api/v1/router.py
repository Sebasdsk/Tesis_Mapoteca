"""
API v1 Main Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, usuarios, cartas, prestamos


# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(cartas.router, prefix="/cartas", tags=["Cartas"])
api_router.include_router(prestamos.router, prefix="/prestamos", tags=["Préstamos"])
