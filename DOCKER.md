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
docker compose up        # levantar en primer plano (Ctrl+C detiene y muestra logs en vivo)
docker compose up -d     # levantar en segundo plano (sin logs en pantalla)
docker compose down      # apagar (la BD conserva sus datos)
```

**Editar código recarga solo** — no reinicies nada:

- `Back/**` → uvicorn recarga automáticamente
- `Front/src/**` → Angular recompila y refresca el navegador

### Ver logs (monitoreo)

Si levantaste con `-d`, o quieres seguir la actividad en otra terminal:

```bash
docker compose logs -f                 # seguir TODOS los servicios (db + back + front)
docker compose logs -f back            # solo el backend
docker compose logs -f front           # solo el frontend
docker compose logs -f --tail=100 back # últimas 100 líneas + en vivo
docker compose logs -t --tail=50       # con timestamps
docker compose logs --since=10m back   # últimos 10 minutos
docker compose logs --no-log-prefix -f back   # sin el prefijo del nombre del contenedor
```

- Para **salir** de `logs -f`: `Ctrl+C` (no detiene los contenedores, solo deja de seguir).
- Si arrancaste con `docker compose up` (primer plano), ya ves los logs en vivo; para
  dejarlo corriendo sin verlos: `Ctrl+P` luego `Ctrl+Q` (detach).
- El backend en dev corre con `DEBUG=true`, así que imprime cada query SQL. En
  producción (`DEBUG=false`) solo salen líneas `INFO` de request, sin SQL.

Solo hay dos casos especiales:

| Caso | Qué hacer |
|---|---|
| Agregaste/quitaste dependencias (`requirements.txt` o `package.json`) | `docker compose down && docker compose up --build -V` (el `-V` recrea el volumen anónimo de `node_modules` del front) |
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
| `ModuleNotFoundError: No module named 'X'` en el back | Cambió `requirements.txt`: `docker compose up --build back` |
| `Cannot find module 'X'` al compilar el front | Cambió `package.json`: `docker compose down && docker compose up --build -V` (recrea `node_modules`) |
