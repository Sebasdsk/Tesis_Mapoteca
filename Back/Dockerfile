# Backend FastAPI - Sistema de Gestión de Mapoteca UAS
# Python 3.12: las dependencias pineadas (psycopg2-binary==2.9.9, pydantic==2.5.3)
# no tienen wheels para 3.13/3.14.
FROM python:3.12-slim

WORKDIR /app

# Dependencias primero (mejor cache de capas en rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Producción: Render inyecta PORT; sin --reload.
# En dev, docker-compose sobreescribe este CMD con migraciones + seed + --reload.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
