# AGENTS.md

## Qué es esto

Sistema de Gestión de Mapoteca UAS (tesis): catálogo y préstamos de cartas topográficas físicas (nomenclatura INEGI). Dos carpetas:

- `Back/` — API FastAPI + PostgreSQL (SQLAlchemy 2.0, Alembic, JWT)
- `Front/` — Angular 20 + Tailwind CSS v4 + Leaflet

Sin CI, sin tests de backend, sin README útil (el de `Front/` es boilerplate del CLI).

## Comandos

### Con Docker (recomendado)

```bash
docker compose up --build   # primera vez o tras cambiar dependencias
docker compose up           # el resto de las veces
docker compose down         # apagar (la BD persiste en el volumen pgdata)
docker compose down -v      # ⚠️ reset total, borra la BD
```

- Levanta `db` (Postgres 16) + `back` (:8000) + `front` (:4200) con hot-reload (volúmenes montados).
- Guía de trabajo diario para humanos en `DOCKER.md`.
- El arranque de `back` corre solo: `alembic upgrade head` → seed `init_db.py` (idempotente) → `uvicorn --reload`.
- Nueva migración: `docker compose exec back alembic revision --autogenerate -m "..."` (el modelo debe estar importado en `alembic/env.py`).
- Si el front no recarga solo al editar: agregar `--poll 2000` al comando de `ng serve`.

### Local sin Docker

Backend (desde `Back/`, venv esperado en `Back/venv`):

```bash
pip install -r requirements.txt
alembic upgrade head          # ANTES del seed; ver gotcha abajo
python -m app.db.init_db      # seed idempotente (admin + cartas de ejemplo)
uvicorn app.main:app --reload # docs en /docs
```

Frontend (desde `Front/`): `npm install && npm start` (`npm test` = Karma/Jasmine).

## Gotchas (verificados, no obvios)

- **`Back/.env` es obligatorio en local** (no existe en el repo): `Settings()` truena al importar sin `DATABASE_URL` y `SECRET_KEY`. Copiar de `Back/.env.example`. Alembic también lo lee (`alembic/env.py` pisa el `sqlalchemy.url` de `alembic.ini`). Con docker compose no hace falta.
- **Orden importa**: `alembic upgrade head` ANTES de `init_db.py`. `init_db` usa `create_all` sin stampear alembic; sobre una BD vacía rompe los `upgrade` posteriores.
- **Login es JSON** (`POST /api/v1/auth/login` con `{username, password}`), no form OAuth2; el `OAuth2PasswordBearer` solo es para la UI de /docs. Admin default: `admin` / `Admin123!`.
- **El front habla a `localhost:8000` incluso en Docker**: Angular corre en el navegador del host, no en la red de Docker. NO cambiar `environment.ts` a `http://back:8000`.
- **Tailwind v4 sin `tailwind.config.js`**: el tema (colores UAS) vive en `@theme` dentro de `src/styles.css` y el contenido se declara con `@source`. Hay dos configs PostCSS duplicadas (`.postcssrc.json` y `postcss.config.js`): editar ambas o consolidar.
- **Leaflet**: la clase `.map-container` (styles.css) fija alto 320px; sin alto explícito el mapa no renderiza.
- **Versiones**: Python 3.12 (no 3.14: `psycopg2-binary==2.9.9` no tiene wheel) y Node 22 (LTS que Angular 20 soporta).

## Arquitectura

- Backend: `app/main.py` → router `/api/v1` con `auth, usuarios, cartas, prestamos, reportes`. Modelos: `Usuario, Carta, Prestamo, ConsultaCatalogo`.
- Auth JWT (HS256, 4h). Roles: `ADMIN, ESTUDIANTE, MAESTRO, EXTERNO`. Endpoints admin-only usan la dependencia `get_current_admin_user`; `get_current_active_user` bloquea si `debe_cambiar_password` (el front redirige a `/cambiar-password` con `passwordChangedGuard`).
- Frontend standalone + signals, sin NgModules: componentes `export default` cargados con `loadComponent`, archivos sin sufijos (`catalogo.ts`, no `catalogo.component.ts`).
- Sesión en `core/service/auth.ts` (localStorage `mapoteca_token`); `authInterceptor` agrega Bearer y hace logout en 401.
- Dominio: `Carta` = carta topográfica física; los enums `TipoCartaEnum` y `DisponibilidadEnum` (FISICA/SOLO_DIGITAL/AMBAS/EXTRAVIADA/DANADA) están duplicados en front y back — mantenerlos sincronizados.

## Convenciones

- Español en código, comentarios, commits y respuestas.
- Prettier (en `Front/package.json`): printWidth 100, singleQuote, parser angular para HTML.
- No hay tests de backend (pytest en requirements pero sin carpeta `tests/`); el front sí tiene specs Karma.
