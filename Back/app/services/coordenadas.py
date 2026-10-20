"""
Utilidades para interpretar coordenadas geodésicas.

Acepta grados decimales (25.25, -109.5) y notación DMS
(25°15'30"N, 25º 15´ N, 109° 00´ W). Devuelve grados decimales
o None si el texto no es una coordenada válida.
"""
import re
from typing import Optional

_DMS_RE = re.compile(
    r"^\s*(?P<sign>[+-])?\s*(?P<deg>\d+(?:[.,]\d+)?)\s*(?:°|º|d)?\s*"
    r"(?:(?P<min>\d+(?:[.,]\d+)?)\s*(?:'|´|′|m)?\s*)?"
    r"(?:(?P<sec>\d+(?:[.,]\d+)?)\s*(?:\"|″|′′|''|´´|s)?\s*)?"
    r"(?P<hem>[NSEWnsew])?\s*$"
)

_HEM_PREFIX_RE = re.compile(r"^([NSEWnsew])\s*(.+)$")


def parse_coordenada(valor, es_longitud: bool = False) -> Optional[float]:
    """Convierte una coordenada en texto a grados decimales."""
    if valor is None:
        return None

    texto = str(valor).strip()
    if not texto:
        return None

    hem_prefijo = None
    prefijo = _HEM_PREFIX_RE.match(texto)
    if prefijo:
        hem_prefijo = prefijo.group(1)
        texto = prefijo.group(2)

    match = _DMS_RE.match(texto)
    if not match:
        return None

    def numero(grupo):
        return float((match.group(grupo) or "0").replace(",", "."))

    grados = numero("deg")
    minutos = numero("min")
    segundos = numero("sec")

    if minutos >= 60 or segundos >= 60:
        return None

    decimal = grados + minutos / 60 + segundos / 3600

    signo = match.group("sign")
    if signo == "-":
        decimal = -decimal

    hemisferio = (match.group("hem") or hem_prefijo or "").upper()
    if hemisferio:
        decimal = abs(decimal)
        if hemisferio in ("S", "W"):
            decimal = -decimal
    elif signo is None and es_longitud and decimal > 0:
        # Convención para México: las longitudes al oeste son negativas.
        decimal = -decimal

    limite = 180 if es_longitud else 90
    if not (-limite <= decimal <= limite):
        return None

    return decimal
