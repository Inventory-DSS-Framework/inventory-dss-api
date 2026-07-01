# Despliegue en Render (capa free)

Guía para desplegar toda la plataforma Inventory DSS en Render. Son **3 servicios**
y **1 base de datos**, cada servicio desde su propio repo de GitHub:

| Componente | Repo | Tipo en Render | Blueprint |
|---|---|---|---|
| Base de datos | — | Postgres (free) | definido en `inventory-dss-api/render.yaml` |
| API backend | `inventory-dss-api` | Web Service (Docker) | `render.yaml` |
| Motor FTGM | `inventory-dss-ftgm-engine` | Web Service (Docker) | `render.yaml` |
| Frontend web | `inventory-dss-web` | Web Service (Node) | `render.yaml` |

> **Nota sobre la capa free:** cada servicio se **duerme tras ~15 min** de inactividad.
> La primera petición tras dormir tarda ~30–60 s en despertar. Para una exposición,
> "calienta" los 3 servicios abriendo sus URLs unos minutos antes.

---

## Orden de despliegue

El orden importa porque unos servicios necesitan la URL de otros.

### 1. Motor FTGM (primero, no depende de nadie)

1. En Render: **New → Blueprint**, conecta el repo `inventory-dss-ftgm-engine`.
2. Render lee su `render.yaml` y crea el servicio `inventory-dss-ftgm-engine`.
3. Espera a que quede *Live*. Copia su URL pública, por ejemplo
   `https://inventory-dss-ftgm-engine.onrender.com`.
4. Verifica: abre `https://…onrender.com/health` → debe responder `{"status":"ok"}`.

### 2. API + Postgres

1. **New → Blueprint**, conecta el repo `inventory-dss-api`.
2. Render crea la base de datos `inventory-dss-db` (free) y el servicio `inventory-dss-api`.
   - `DATABASE_URL` se inyecta solo desde la base de datos.
   - `JWT_SECRET_KEY` se genera solo.
   - `STORAGE_BACKEND=db` → los archivos subidos se guardan en Postgres (no se pierden).
3. En el dashboard del servicio API, pestaña **Environment**, define las 2 variables
   marcadas como *sync: false*:
   - `FTGM_ENGINE_BASE_URL` = URL del FTGM del paso 1 **+ `/api/v1`**
     → `https://inventory-dss-ftgm-engine.onrender.com/api/v1`
   - `CORS_ORIGINS` = (temporal por ahora) `http://localhost:3000`
     → lo actualizarás en el paso 4 con la URL real del frontend.
4. El arranque corre `alembic upgrade head` automáticamente (crea todas las tablas,
   incluida `stored_blobs`). Verifica `https://<api>.onrender.com/health`.

### 3. Frontend web

1. **New → Blueprint**, conecta el repo `inventory-dss-web`.
2. En **Environment**, define:
   - `NEXT_PUBLIC_API_BASE_URL` = URL del API **+ `/api/v1`**
     → `https://inventory-dss-api.onrender.com/api/v1`
   - ⚠️ Esta variable se **hornea en el build**. Si la cambias después, usa
     **Manual Deploy → Clear build cache & deploy**.
3. Espera el build (`npm install && npm run build`) y que quede *Live*.
   Copia la URL, por ejemplo `https://inventory-dss-web.onrender.com`.

### 4. Cerrar el círculo (CORS)

1. Vuelve al servicio **API → Environment**.
2. Cambia `CORS_ORIGINS` a la URL del frontend (sin barra final):
   `https://inventory-dss-web.onrender.com`
3. Guarda → el API redepliega solo. Listo.

---

## Mapa de comunicación

```
Navegador ──► Web (Next.js, Render)
Navegador ──► API  (NEXT_PUBLIC_API_BASE_URL, con CORS permitido)
API       ──► FTGM (FTGM_ENGINE_BASE_URL, servidor a servidor)
API       ──► Postgres (DATABASE_URL, inyectado por Render)
```

## Variables por servicio (resumen)

**API** (`inventory-dss-api`)
- `DATABASE_URL` — auto (desde la DB)
- `JWT_SECRET_KEY` — auto (generado)
- `STORAGE_BACKEND=db`, `APP_ENV=production`, `APP_DEBUG=false`
- `FTGM_ENGINE_TIMEOUT_SECONDS=90` — tolera el cold start del FTGM
- `FTGM_ENGINE_BASE_URL` — manual (URL del FTGM + `/api/v1`)
- `CORS_ORIGINS` — manual (URL del web)

**FTGM** (`inventory-dss-ftgm-engine`)
- Ninguna obligatoria (solo `APP_ENV`/`APP_DEBUG` opcionales).

**Web** (`inventory-dss-web`)
- `NEXT_PUBLIC_API_BASE_URL` — manual (URL del API + `/api/v1`), **build-time**
- `NODE_VERSION=20`

---

## Por qué el almacenamiento va en Postgres

En la capa free el disco del contenedor es **efímero**: se borra en cada reinicio,
redeploy o al despertar de la siesta. El flujo de ingesta sube el CSV en un paso y
lo **relee** en el paso "Preparar dataset" (una petición posterior). Si el archivo
viviera en disco, desaparecería entre pasos y "Preparar" fallaría.

Por eso `STORAGE_BACKEND=db`: los bytes del archivo se guardan en la tabla
`stored_blobs` de Postgres (que sí es persistente), y sobreviven a reinicios y
redeploys. Para desarrollo local sin base de datos puedes usar `STORAGE_BACKEND=local`.
