"""
FastAPI main application
Sistema de Gestión de Mapoteca UAS
"""
import time

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import setup_logging, get_logger
from app.core.dependencies import get_db
from app.api.v1.router import api_router


# Configurar logging antes que nada
setup_logging()
logger = get_logger("app")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de catalogación y administración digital para mapoteca física universitaria",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting (SlowAPI)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Loguea método, ruta, status y duración de cada request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Manejador global: loguea la traza completa pero no la expone al cliente
    en producción.
    """
    logger.exception("unhandled_exception path=%s", request.url.path)
    detail = str(exc) if settings.DEBUG else "Error interno del servidor"
    return JSONResponse(status_code=500, content={"detail": detail})


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1"
    }


# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check: valida que la app y la base de datos respondan."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("healthcheck_db_failed")
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    return {"status": "healthy", "database": "ok"}
