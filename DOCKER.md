# Guía de trabajo con Docker — Mapoteca UAS

Stack completo de desarrollo: PostgreSQL 16 + API FastAPI (:8000) + Angular (:4200), todo con hot-reload.

## Requisitos

- Docker + Docker Compose plugin (`docker compose version`)
- Tu usuario en el grupo `docker` (si `docker ps` da "permission denied"):
  ```bash
  sudo usermod -aG docker $USER   # luego cierra y vuelve a abrir sesión
  ```

## Primer arranque

```bash
docker compose up --build
```

Esto levanta, en orden:

1. **db** — Postgres 16, crea la base `mapoteca_db` (datos persisten en el volumen `pgdata`)
2. **back** — espera a que db esté sana y luego corre automáticamente:
   `alembic upgrade head` (migraciones) → `init_db.py` (seed: admin + cartas de ejemplo, idempotente) → `uvicorn --reload`
3. **front** — `ng serve --host 0.0.0.0`

Cuando veas `Compiled successfully` en el front y `Application startup complete` en el back:

- App: http://localhost:4200 → login `admin` / `Admin123!`
- API docs (Swagger): http://localhost:8000/docs

Los builds siguientes ya no necesitan `--build` (queda en caché): usa solo `docker compose up`.

## Flujo diario

```bash
docker compose up        # levantar (Ctrl+C para detener)
docker compose up -d     # levantar en segundo plano
docker compose down      # apagar (la BD conserva sus datos)
docker compose logs -f back    # ver logs del back en vivo (también: db, front)
```

**Editar código recarga solo** — no reinicies nada:

- `Back/**` → uvicorn recarga automáticamente
- `Front/src/**` → Angular recompila y refresca el navegador

Solo hay dos casos especiales:

| Caso | Qué hacer |
|---|---|
| Agregaste/quitaste dependencias (`requirements.txt` o `package.json`) | `docker compose down && docker compose up --build` |
| Creaste o cambiaste un modelo de SQLAlchemy | `docker compose exec back alembic revision --autogenerate -m "descripcion"` y reinicia el back (al arrancar aplica solo el `upgrade head`) |

## Comandos útiles

```bash
docker compose ps                              # estado de los contenedores
docker compose exec back bash                  # shell dentro del back
docker compose exec db psql -U mapoteca_user mapoteca_db   # SQL directo a la BD
docker compose exec back alembic history       # ver migraciones
docker compose down -v                         # ⚠️ RESET TOTAL: borra la BD y sus datos
```

## Notas importantes

- **`environment.ts` siempre apunta a `http://localhost:8000/api/v1`**, incluso con Docker. Angular corre en tu navegador, no dentro de la red de Docker — nunca uses `http://back:8000` ahí.
- Credenciales de la BD (definidas en `docker-compose.yml`): `mapoteca_user` / `mapoteca_pass_2024` / `mapoteca_db`.
- El seed es idempotente: arrancar mil veces no duplica datos.
- Para desarrollo sin Docker ver `Back/.env.example` y la sección "Local sin Docker" de `AGENTS.md`.

## Troubleshooting

| Síntoma | Solución |
|---|---|
| `permission denied ... docker.sock` | Falta estar en el grupo `docker` (ver Requisitos) |
| `port is already allocated` (4200/8000/5432) | Otro proceso usa el puerto: `docker compose down`, o mata el proceso local (ej. Postgres local: `sudo systemctl stop postgresql`) |
| El back falla en migraciones tras cambios raros de esquema | `docker compose down -v && docker compose up` (reset de BD) |
| El front no recarga al editar | Agregar `--poll 2000` al comando de `ng serve` en `Front/Dockerfile` y rebuild |
| Cambiaste `package.json` y el front no ve la dep nueva | `docker compose up --build front` |
