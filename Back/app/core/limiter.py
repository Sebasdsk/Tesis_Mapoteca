"""
Rate limiting compartido (SlowAPI).

La clave es la IP del cliente. Detrás del proxy de Vercel, la IP real llega en
X-Forwarded-For; tomamos el primer valor. Si no hay cabecera, usamos el host
directo de la conexión (get_remote_address).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip)
