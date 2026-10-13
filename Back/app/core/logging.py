"""
Configuración centralizada de logging.
"""
import logging
from logging.config import dictConfig

from app.core.config import settings


def setup_logging() -> None:
    """
    Configura logging a stdout con formato legible y nivel según DEBUG.

    - development (DEBUG=true): nivel DEBUG
    - production: nivel INFO
    """
    level = "DEBUG" if settings.DEBUG else "INFO"

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            "uvicorn.error": {"level": level, "handlers": ["console"], "propagate": False},
            "uvicorn.access": {"level": level, "handlers": ["console"], "propagate": False},
        },
    })


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
