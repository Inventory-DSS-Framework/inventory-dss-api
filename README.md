# Inventory DSS API

Backend principal de la plataforma **Inventory Optimization DSS Platform**, una solución web de soporte de decisiones para la optimización de inventarios en MYPEs retail de Lima Metropolitana.

Este repositorio implementa el núcleo transaccional y analítico de la plataforma. Su responsabilidad es recibir datos operativos, preparar información, orquestar predicciones, calcular KPIs, generar recomendaciones y exponer APIs para el frontend.

## Decisión arquitectónica principal

Este backend se implementa como un **monolito modular** con **arquitectura hexagonal**.

Esto significa que:

* Existe un solo backend desplegable.
* Los módulos no son microservicios.
* Cada módulo está separado internamente por responsabilidades.
* Cada módulo respeta capas hexagonales.
* La lógica de dominio no depende de frameworks.
* La infraestructura se conecta mediante adapters.
* El FTGM Engine se consume como un servicio externo mediante un adapter.

## Por qué no microservicios por módulo

No se crearán repositorios separados para:

* Auth.
* Products.
* Sales.
* Inventory.
* Forecasting.
* KPIs.
* Recommendations.

Estos módulos pertenecen al mismo backend porque forman parte del núcleo funcional de la plataforma DSS. Separarlos como microservicios aumentaría la complejidad innecesariamente para el alcance académico y operativo del proyecto.

## Rol dentro del sistema multi-repositorio

| Repositorio                 | Responsabilidad                            |
| --------------------------- | ------------------------------------------ |
| `inventory-dss-web`         | Frontend Next.js                           |
| `inventory-dss-api`         | Backend FastAPI monolito modular hexagonal |
| `inventory-dss-ftgm-engine` | Motor analítico FTGM desacoplado           |
| `inventory-dss-infra`       | Infraestructura y despliegue               |
| `inventory-dss-docs`        | Documentación académica y arquitectónica   |

## Módulos del backend

El backend contiene los siguientes módulos:

| Módulo           | Responsabilidad                                                       |
| ---------------- | --------------------------------------------------------------------- |
| Auth             | Autenticación, JWT, sesiones, roles y permisos                        |
| Companies        | Gestión de MYPEs, usuarios por empresa y configuración                |
| Products         | Catálogo de productos, SKU, categorías, costos y parámetros           |
| Sales            | Registro e historial de ventas observadas                             |
| Inventory        | Movimientos, stock actual, snapshots y eventos de stockout            |
| Ingestion        | Carga, validación y mapeo de archivos CSV/Excel                       |
| Data Preparation | Limpieza, normalización, outliers, stockout flags y series preparadas |
| Forecasting      | Orquestación de ejecuciones de predicción y consumo del FTGM Engine   |
| KPIs             | Cálculo de cobertura, riesgo de quiebre, rotación y sobrestock        |
| Recommendations  | Generación de sugerencias accionables de reposición                   |
| Reports          | Reportes de pronósticos, KPIs y recomendaciones                       |
| Notifications    | Alertas internas, correos futuros y eventos de notificación           |
| Billing          | Planes, suscripciones y pagos futuros                                 |

## Arquitectura hexagonal

Cada módulo debe respetar esta estructura:

```text
module/
├── domain/
├── application/
│   └── use_cases/
├── infrastructure/
│   ├── persistence/
│   └── adapters/
└── presentation/
```

### Domain

Contiene:

* Entidades.
* Value objects.
* Reglas de negocio.
* Servicios de dominio.
* Eventos de dominio.
* Excepciones.
* Interfaces de repositorio cuando corresponda.

No debe importar:

* FastAPI.
* SQLAlchemy.
* Supabase.
* HTTP clients.
* Frameworks externos.

### Application

Contiene:

* Casos de uso.
* DTOs.
* Puertos.
* Servicios de aplicación.
* Orquestación de acciones del negocio.

### Infrastructure

Contiene:

* Modelos ORM.
* Repositorios SQLAlchemy.
* Mappers.
* Adapters externos.
* Implementaciones concretas de puertos.

### Presentation

Contiene:

* Routers FastAPI.
* Schemas Pydantic.
* Dependencias HTTP.
* Contratos de entrada y salida.

## Reglas de dependencia

```text
presentation → application → domain
infrastructure → application/domain ports
domain → no depende de frameworks
```

## Adapters principales

| Adapter                    | Responsabilidad                                             |
| -------------------------- | ----------------------------------------------------------- |
| Database Adapter           | Conectar con PostgreSQL/Supabase                            |
| Dataset Repository Adapter | Guardar archivos originales, datasets preparados y reportes |
| FTGM Adapter               | Consumir el servicio externo `inventory-dss-ftgm-engine`    |
| Notification Adapter       | Enviar alertas y correos futuros                            |
| Payment Adapter            | Integrar pasarela de pago futura                            |
| Queue Adapter              | Soportar procesos asíncronos futuros                        |

## Relación con FTGM Engine

El backend no contiene el algoritmo matemático principal del FTGM. El módulo `forecasting` prepara y envía series temporales al servicio externo `inventory-dss-ftgm-engine` mediante un adapter HTTP.

Flujo conceptual:

```text
Prepared Time Series
        ↓
Forecasting Module
        ↓
FTGM Adapter
        ↓
FTGM Engine
        ↓
Forecast Results + Metrics
        ↓
KPIs + Recommendations
```

## DSS: Sistema de Soporte de Decisiones

Este backend no solo registra datos. Su objetivo es transformar datos operativos en información accionable:

* Pronóstico de demanda.
* Cobertura de inventario.
* Riesgo de quiebre de stock.
* Riesgo de sobrestock.
* Prioridad de reposición.
* Cantidad sugerida de compra.
* Reportes para toma de decisiones.

## Estado actual

Este repositorio se encuentra en fase inicial. Contiene estructura base, configuración mínima de FastAPI y documentación arquitectónica inicial.
