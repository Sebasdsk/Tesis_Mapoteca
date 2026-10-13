# Despliegue a producción — Mapoteca UAS

Topología: **Vercel** (front Angular) → proxy same-origin `/api/*` → **Render**
(back FastAPI) → **Neon** (PostgreSQL). El proxy same-origin hace que la cookie
de sesión funcione como first-party y elimina CORS.

## 1. Base de datos (Neon)

1. Crear proyecto/DB en https://neon.tech.
2. Copiar la cadena de conexión y **agregar `?sslmode=require`**, por ejemplo:
   ```
   postgresql://usuario:pass@ep-xxx.region.aws.neon.tech/mapoteca_db?sslmode=require
   ```
   Se usará como `DATABASE_URL` en Render.

## 2. Backend (Render)

1. New → Web Service → repo → **Root Directory: `Back`** → Runtime: **Docker**.
   El `Back/Dockerfile` ya arranca con `uvicorn` en `$PORT` (sin `--reload`).
2. **Pre-Deploy Command**:
   ```
   alembic upgrade head
   ```
3. **Start Command** (crea admin si no existe; sin datos demo en producción):
   ```
   python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Environment Variables**:
   | Variable | Valor |
   |---|---|
   | `ENVIRONMENT` | `production` |
   | `DEBUG` | `false` |
   | `DATABASE_URL` | cadena de Neon con `?sslmode=require` |
   | `SECRET_KEY` | genera con `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `ALLOWED_ORIGINS` | `https://<tu-proyecto>.vercel.app` |
   | `ADMIN_USERNAME` | usuario admin deseado |
   | `ADMIN_EMAIL` | email admin |
   | `ADMIN_PASSWORD` | contraseña fuerte (no la default) |

   Con `ENVIRONMENT=production`, el arranque **falla** si `SECRET_KEY` es débil o
   `ADMIN_PASSWORD` es la default (fail-fast en `app/core/config.py`).

5. Anota la URL del servicio, p. ej. `https://mapoteca-api.onrender.com`.

## 3. Frontend (Vercel)

1. Importar el repo → **Root Directory: `Front`** → Framework: **Angular**.
2. Editar `Front/vercel.json` y reemplazar `TU-BACKEND.onrender.com` por la URL
   real de Render. El rewrite `/api/(.*)` hace de proxy same-origin.
3. Build: `npm run build`; salida: `dist/Proyecto_Tesis/browser`.
   La configuración `production` de `angular.json` ya reemplaza `environment.ts`
   por `environment.prod.ts` (que usa `apiUrl: '/api/v1'`).

## 4. Verificaciones post-deploy

- `GET https://<api>.onrender.com/health` → `{"status":"healthy"}`.
- Abrir el front, iniciar sesión como admin → debe redirigir y cargar catálogo.
- Recargar la página: la sesión debe persistir (refresh vía cookie).
- Subir un CSV pequeño en Carga Masiva (ojo: Vercel proxy limita el tamaño del
  body, ~4.5 MB).

## 5. Notas

- Render free se suspende por inactividad (~15 min): usar keep-alive (UptimeRobot)
  o plan pago para evitar cold starts en el login.
- Si el `Set-Cookie` no atraviesa bien el proxy de Vercel, plan B es dominio
  propio (`app.tudominio.com` + `api.tudominio.com`) con `COOKIE_SAMESITE=lax`.
