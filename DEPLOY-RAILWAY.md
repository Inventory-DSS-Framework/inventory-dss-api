# Despliegue en Railway

Un **proyecto** de Railway con 4 piezas. Cada repo es un servicio; todo se construye con
Dockerfile y las migraciones corren solas al arrancar el API.

| Pieza | Repo | Cómo lo construye Railway |
|---|---|---|
| Base de datos | — | Plugin **PostgreSQL** de Railway |
| Motor FTGM | `inventory-dss-ftgm-engine` | `Dockerfile` (bindea `$PORT`, healthcheck `/health`) |
| API backend | `inventory-dss-api` | `Dockerfile` (migra, carga la demo si `SEED_DEMO=true`, bindea `$PORT`) |
| Frontend web | `inventory-dss-web` | **`Dockerfile.prod`** vía `railway.json` (build de producción de Next.js) |

> Railway no tiene tier gratis permanente: trial con crédito y luego plan **Hobby
> (US$5/mes + uso)**. 3 servicios + Postgres entran cómodos en Hobby para una demo.

---

## 1. PostgreSQL
**New → Database → PostgreSQL.** Railway crea `DATABASE_URL` (`postgresql://…`); el API
la normaliza sola al driver psycopg.

## 2. Motor FTGM
1. **New → GitHub Repo → `inventory-dss-ftgm-engine`.**
2. **Settings → Networking → Generate Domain.** Copia la URL, p. ej.
   `https://ftgm-production-xxxx.up.railway.app`.
3. No necesita variables. Verifica `https://<ftgm>/health` → `{"status":"ok"}`.

> Se usa la URL **pública** del motor (no `*.railway.internal`): la red privada de
> Railway es IPv6 y uvicorn escucha en IPv4 (`0.0.0.0`).

## 3. API
1. **New → GitHub Repo → `inventory-dss-api`.**
2. **Variables:**
   ```
   DATABASE_URL                = ${{Postgres.DATABASE_URL}}
   FTGM_ENGINE_BASE_URL        = https://<tu-ftgm>.up.railway.app/api/v1
   FTGM_ENGINE_TIMEOUT_SECONDS = 90
   JWT_SECRET_KEY              = <cadena larga y aleatoria>
   APP_ENV                     = production
   APP_DEBUG                   = false
   STORAGE_BACKEND             = db
   CORS_ORIGIN_REGEX           = https://.*\.up\.railway\.app
   SEED_DEMO                   = true
   ```
   - `${{Postgres.DATABASE_URL}}` es una referencia de Railway: escríbela tal cual (con
     el nombre de tu servicio Postgres).
   - `CORS_ORIGIN_REGEX` deja pasar al web desde cualquier dominio `*.up.railway.app`,
     así no dependes del orden de despliegue. Si luego usas un dominio propio, agrégalo
     en `CORS_ORIGINS` (lista separada por comas).
   - `SEED_DEMO=true` carga la demo **una sola vez** en la base vacía (ver abajo). Es
     seguro dejarlo: si la demo ya existe, no hace nada.
3. **Generate Domain.** El primer arranque migra y siembra la demo (~10–60 s). Verifica
   `https://<api>/health` → `{"status":"ok"}`. El healthcheck espera hasta 300 s.

## 4. Web
1. **New → GitHub Repo → `inventory-dss-web`.** El `railway.json` usa `Dockerfile.prod`.
2. **Variables:**
   ```
   NEXT_PUBLIC_API_BASE_URL = https://<tu-api>.up.railway.app/api/v1
   ```
   ⚠️ Se **hornea en el build**. Si la cambias, haz **Redeploy**.
3. **Generate Domain** → abre la URL. Listo.

---

## Datos de la demo (`SEED_DEMO=true`)
`scripts/bootstrap_demo.py` crea, solo si no existe:

| | |
|---|---|
| Empresa | **PetHouse Lima** — plan **Premium** activo (1 año) |
| Dueño | `demo@pethouse.pe` / `Demo12345!` |
| Vendedora (solo caja) | `lramos` / `Ventas2026!` |
| Catálogo | 12 productos SKU-001…012 con código de barras EAN-13 (`7751234500013`…), árbol Perros/Gatos |
| Historia | ventas diarias 2022–2024 + 2025→ayer con tickets POS, compras a 3 proveedores, movimientos de stock y quiebres |

Probado en base vacía: ~18 000 ventas, 360 tickets, 169 compras en ~6 s.
Para regenerar solo la historia reciente: `python scripts/seed_demo_history.py` (desde
**Railway → API → Shell**).

## Mapa de comunicación
```
Navegador ─► Web  (Railway)
Navegador ─► API  (NEXT_PUBLIC_API_BASE_URL, CORS por CORS_ORIGIN_REGEX)
API       ─► FTGM (FTGM_ENGINE_BASE_URL, URL pública)
API       ─► Postgres (DATABASE_URL, referencia del plugin)
```

## Checklist
- [x] Dockerfiles del API/FTGM bindean `$PORT`; dependencias en capa aparte (builds rápidos)
- [x] `Dockerfile.prod` del web — `next build` de producción verificado (29 rutas, TypeScript limpio)
- [x] `railway.json` en los 3 repos (API con healthcheck de 300 s por la siembra inicial)
- [x] Migraciones automáticas (`alembic upgrade head`) al arrancar el API
- [x] Demo auto-cargable e idempotente (`SEED_DEMO=true`)
- [x] Logs SQL apagados por defecto (`APP_DEBUG=false`)
- [ ] Variables puestas en el dashboard (pasos 3 y 4)

## Problemas comunes
| Síntoma | Causa / solución |
|---|---|
| Login falla con "Failed to fetch" | `NEXT_PUBLIC_API_BASE_URL` mal escrita o sin `/api/v1` → corrige y **Redeploy** del web |
| Error CORS en la consola | Falta `CORS_ORIGIN_REGEX` (o tu dominio en `CORS_ORIGINS`) en el API |
| Pronóstico queda en "failed" | `FTGM_ENGINE_BASE_URL` sin `/api/v1` o motor dormido; revisa `https://<ftgm>/health` |
| No aparece la demo | `SEED_DEMO` no es `true`, o mira los logs del API (`bootstrap_demo: …`) |
