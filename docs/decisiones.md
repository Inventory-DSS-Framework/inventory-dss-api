# Decisiones de arquitectura — Backend (Inventory DSS API)

Registro de las decisiones técnicas tomadas durante la implementación. Cada entrada
documenta el contexto, la decisión y la razón, para que sea defendible en la tesis.

## ADR-001 — SQLAlchemy 2.0 con sesiones síncronas

**Contexto.** El backend es un monolito modular hexagonal. Su carga real es CRUD ligero
y orquestación; la única operación pesada (forecasting) se delega a un servicio externo
(FTGM Engine) por HTTP. La escala objetivo son MYPEs de Lima (baja concurrencia).

**Decisión.** Usar **SQLAlchemy 2.0** (estilo `Mapped`/`mapped_column`) con **sesiones
síncronas** y driver `psycopg` v3. Las migraciones se gestionan con **Alembic**. El modelo
ORM se mantiene **separado** de la entidad de dominio mediante mappers.

**Razones.**
- SQLAlchemy + Alembic es el estándar maduro con mejor soporte de migraciones.
- Separar ORM de dominio respeta la regla hexagonal (el dominio no depende de la
  persistencia), que es el argumento arquitectónico central de la tesis. Por eso se
  descartó SQLModel, que fusiona Pydantic + ORM en una sola clase.
- El modo síncrono es más simple, mejor documentado y con menos trampas (greenlet, libs
  async-compatibles, Alembic async, tests async). FastAPI ejecuta los endpoints síncronos
  en un threadpool, así que no se pierde concurrencia para esta escala.

## ADR-002 — Forecasting como trabajo en segundo plano (no async global)

**Contexto.** La llamada al FTGM Engine es la única operación lenta y de I/O potencialmente
largo. Resolverla dentro del request bloquearía la petición.

**Decisión.** El forecasting se ejecuta como **trabajo en segundo plano con polling de
estado**, no convirtiendo el backend a async. El patrón es: el endpoint de ejecución crea
el `ForecastRun`, responde **202** de inmediato, un worker procesa en background y el
cliente consulta el estado por `/forecast-runs/{run_id}/status`. Los endpoints
`execute`, `status`, `cancel`, `retry` y `logs` ya existen para soportarlo.

**Razones.**
- Aísla la única operación lenta sin imponer el coste de async a las 288 rutas.
- En la primera fase el worker será `BackgroundTasks` de FastAPI; a futuro se sustituye por
  una cola real (Celery/RQ/Arq) detrás del `QueuePort` ya definido en
  `app/shared/infrastructure/ports.py`. La frontera (el puerto) no cambia.

## ADR-003 — Multi-tenancy por `company_id`

**Decisión.** Las entidades de negocio cuelgan de una empresa vía `CompanyOwnedMixin`
(`company_id` indexado). El acceso se valida en la capa de presentación con
`require_company_access`, que compara el `company_id` de la ruta contra el de los claims
del JWT del usuario autenticado.
