"""
Lógica de referencias oficiales del INEGI.
"""
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.carta import Carta
from app.models.fuente_inegi import FuenteInegi


def validar_url_inegi(url: str) -> str:
    """
    Valida que la URL pertenezca al dominio oficial del INEGI y use https.
    Devuelve la URL normalizada (sin espacios). Lanza ValueError si es inválida.
    """
    url = (url or "").strip()
    if any(caracter.isspace() or ord(caracter) < 32 for caracter in url):
        raise ValueError("La URL no debe contener espacios ni caracteres de control")
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if parsed.scheme != "https":
        raise ValueError("La URL debe usar https")
    if not (host == "inegi.org.mx" or host.endswith(".inegi.org.mx")):
        raise ValueError("La URL debe pertenecer al dominio inegi.org.mx")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("La URL no debe contener credenciales")
    if parsed.port not in (None, 443):
        raise ValueError("La URL debe usar el puerto HTTPS estándar")

    return url


def resolver_referencia(carta: Carta, db: Session) -> Optional[dict]:
    """
    Resuelve la referencia INEGI de una carta, en este orden:
      1. Si la carta tiene url_inegi (específica), se usa esa (origen: carta).
      2. Si no, se busca en fuentes_inegi por (escala, tipo_carta) (origen: catalogo).
      3. Si no hay coincidencia, None.
    """
    if carta.url_inegi:
        return {
            "url": carta.url_inegi,
            "nombre": None,
            "origen": "carta",
            "estado": None,
        }

    fuente = db.query(FuenteInegi).filter(
        FuenteInegi.escala == carta.escala,
        FuenteInegi.tipo_carta == carta.tipo_carta,
    ).first()

    if fuente:
        return {
            "url": fuente.url,
            "nombre": fuente.nombre,
            "origen": "catalogo",
            "estado": fuente.estado_enlace,
        }

    return None
