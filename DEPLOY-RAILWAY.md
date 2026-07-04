# Despliegue en Railway

Cada repo es un servicio en Railway. El código ya está listo: los Dockerfiles del API
y el motor FTGM bindean `$PORT`, el web tiene un `Dockerfile.prod` de producción
(seleccionado por su `railway.json`), el almacenamiento de archivos vive en Postgres
(sobrevive reinicios) y `DATABASE_URL` se normaliza solo al driver psycopg.

| Componente | Repo | Cómo lo construye Railway |
|---|---|---|
| Base de datos | — | Plugin **PostgreSQL** de Railway |
| Motor FTGM | `inventory-dss-ftgm-engine` | Dockerfile (bindea `$PORT`) |
| API backend | `inventory-dss-api` | Dockerfile (migra + bindea `$PORT`) |
| Frontend web | `inventory-dss-web` | **`Dockerfile.prod`** (vía `railway.json`) |

> Railway **ya no tiene tier gratis permanente**: da un trial (~$5 de crédito) y luego
> pide plan **Hobby ($5/mes)**. Con 3 servicios + Postgres, el trial se agota rápido.

---

## Orden de despliegue

Crea **un proyecto** en Railway y dentro añade los servicios en este orden.

### 1. PostgreSQL
**New → Database → PostgreSQL.** Railway crea la variable `DATABASE_URL` (formato
`postgresql://…`) que el API consumirá por referencia.

### 2. Motor FTGM
1. **New → GitHub Repo → `inventory-dss-ftgm-engine`.** Railway detecta el Dockerfile.
2. **Settings → Networking → Generate Domain.** Copia la URL pública, p.ej.
   `https://ftgm-production-xxxx.up.railway.app`.
3. No necesita más variables. Verifica `…/health` → `{"status":"ok"}`.

> **Por qué dominio público y no red privada:** la red privada de Railway
> (`*.railway.internal`) es IPv6 y uvicorn escucha en IPv4 (`0.0.0.0`). Usar la URL
> pública del FTGM para la llamada API→FTGM evita ese problema sin tocar nada.

### 3. API
1. **New → GitHub Repo → `inventory-dss-api`.**
2. **Variables** (Settings → Variables):
   ```
   DATABASE_URL              = ${{Postgres.DATABASE_URL}}
   FTGM_ENGINE_BASE_URL      = https://<tu-ftgm>.up.railway.app/api/v1
   FTGM_ENGINE_TIMEOUT_SECONDS = 90
   JWT_SECRET_KEY            = <una-cadena-larga-aleatoria>
   STORAGE_BACKEND           = db
   APP_ENV                   = production
   APP_DEBUG                 = false
   CORS_ORIGINS              = http://localhost:3000   (temporal; se actualiza en el paso 5)
   ```
   `${{Postgres.DATABASE_URL}}` es una **referencia de variable** de Railway: escríbela
   tal cual, apuntando al nombre de tu servicio Postgres.
3. **Generate Domain.** El arranque corre `alembic upgrade head` solo. Verifica `…/health`.

### 4. Web
1. **New → GitHub Repo → `inventory-dss-web`.** El `railway.json` hace que use
   `Dockerfile.prod` (build de producción, no el dev).
2. **Variables:**
   ```
   NEXT_PUBLIC_API_BASE_URL = https://<tu-api>.up.railway.app/api/v1
   ```
   ⚠️ Esta variable se **hornea en el build** (Railway la pasa como build-arg). Si la
   cambias después, hay que **redeploy**.
3. **Generate Domain.** Copia la URL del web.

### 5. Cerrar CORS
Vuelve al servicio **API → Variables** y pon `CORS_ORIGINS` a la URL del web:
```
CORS_ORIGINS = https://<tu-web>.up.railway.app
```
Guarda → el API redepliega solo. Listo.

---

## Mapa de comunicación
```
Navegador ─► Web (Railway)
Navegador ─► API   (NEXT_PUBLIC_API_BASE_URL, con CORS permitido)
API       ─► FTGM  (FTGM_ENGINE_BASE_URL, URL pública)
API       ─► Postgres (DATABASE_URL, referencia del plugin)
```

## Cargar datos (base de datos nueva)
Es el mismo flujo por la UI: **Registro** (crea la empresa) → **Catálogo** (crea los 12
productos SKU-001…012) → **Ventas** (sube `ventas.csv`) → **Preparar dataset** (siembra
ventas + stock) → **Pronóstico** (auto-genera KPIs, recomendaciones y notificaciones).
Para sembrar los productos por SQL, conéctate a la `DATABASE_URL` del Postgres de
Railway y corre el mismo INSERT que usas en local.

## Checklist de "listo para subir"
- [x] Dockerfiles del API/FTGM bindean `$PORT`
- [x] `inventory-dss-web/Dockerfile.prod` (build de producción, `$PORT`)
- [x] `railway.json` en los 3 repos (web apunta a `Dockerfile.prod`; API/FTGM con healthcheck `/health`)
- [x] `DATABASE_URL` se normaliza a psycopg en `app/config.py`
- [x] Almacenamiento en Postgres (`STORAGE_BACKEND=db`)
- [ ] Variables puestas en el dashboard (paso 3, 4 y 5)
