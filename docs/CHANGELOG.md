# Changelog — CallQA AI

Cambios relevantes. Formato: descripción (commit). Lo más nuevo arriba.

## Rediseño premium de indicadores y UX
- `Sistema de dataviz de marca` (`frontend/components/dashboard/viz.tsx`): **ScoreGauge**
  (anillo de score), **Sparkline**, **Donut**, **MiniProgress**, **DeltaPill** y
  **BrandTooltip**; **StatCard** (KPI con delta + sparkline + progreso a meta),
  **SectionHeader/Eyebrow** y **CallsTrendChart** (área con gradiente + línea de meta).
- `Dashboard del jefe rediseñado`: toolbar compacto con **control segmentado** de
  periodo, banda de resumen con **gauge héroe** + StatCards, tendencias (área + **donut**
  de distribución), **tabla de campañas** con barras inline y delta chips, **alertas con
  franja de severidad** e iconos por tipo, rankings y dinámica de conversación.
  `/mi-panel` (percentil con barra de posición) y `calls/[id]` (gauge de score) alineados.
  Todo fiel a la identidad Minsait (paleta, chaflanes, titulares en minúscula, ForFuture Sans).
- `Banner de prototipo eliminado` de la UI (layout + login). El header HTTP
  `X-Prototype-Notice` se conserva.

> 🔑 **Nota de operación:** la IA en producción depende de `GROQ_API_KEY` en **Render**
> (`sync: false`, se pone a mano en el dashboard). Si Groq devuelve `401`, actualízala con
> la key válida; `git push` no la cambia.

## Fase 2 — Analítica de alto impacto
- `Dashboard del jefe`: fila de **alertas accionables** (asesor bajo umbral, caída de
  tendencia, llamadas en banda roja, claim prohibido / frases obligatorias omitidas,
  anomalía de sentimiento), **KPIs por campaña** con delta vs periodo previo (% rojas,
  sentimiento, duración, volumen), **radar de dimensiones del equipo** y **top problemas
  recurrentes** (agregación de `Analysis.recommendations`).
- `Métricas de conversación` deterministas ($0) desde `Transcription.segments`:
  talk-to-listen ratio, % de silencio/dead-air, monólogo más largo del agente,
  palabras/min y turnos/min. Servicio `conversation_metrics_service.py`, columna
  `Call.conversation_metrics` (**migración 0006**), cálculo en el pipeline y **al vuelo**
  para llamadas antiguas. Se exponen en el detalle de llamada y agregadas en el dashboard.
- `Vista asesor (/mi-panel)`: **percentil anónimo** dentro de su campaña (oculto bajo
  `qa_min_calls_ranking`), **"qué cambiar"** (recomendaciones agregadas por dimensión con
  evidencia de un segmento real) y **desglose por campaña** con cumplimiento de la nota de
  producto (cobertura de frases obligatorias, claims prohibidos).
- `Endpoints nuevos` bajo `/dashboard`: `/by-campaign`, `/alerts`, `/top-recommendations`
  (todos `[manager]`), `/agents/{id}/percentile` y `/agents/{id}/recommendations` (`[scoped]`).
  `/summary` extendido con `team_dimension_averages`, `avg_duration_seconds`,
  `red_call_count`/`red_call_pct` y `conversation_summary`.
- `Compliance de nota de producto` (`compliance_service.py`): comprobación determinista
  best-effort de frases obligatorias y claims prohibidos contra lo que dijo el agente.
- `Frontend`: editor de **umbrales QA** en `/settings`, UI **"crear acceso de asesor"** en
  `agents/[id]` (`POST /agents/{id}/login`), métricas de conversación en `calls/[id]`.
  Componentes en `frontend/components/dashboard/insights.tsx`; hooks en `lib/queries.ts`.
- `Banner de prototipo eliminado`: se retira el banner "Vista previa / entorno de
  evaluación" de la UI (layout y login). El header HTTP `X-Prototype-Notice` se conserva.
- `Tests`: +17 (`backend/tests/test_dashboard_phase2.py`), total **78**.

## Fix cold-start (producción gratis)
- `Cold-start mitigado`: el plan gratis de Render duerme el backend tras ~15 min
  (arranque en frío ~50 s, que se veía como "error de API"). Se añade GitHub Action
  `.github/workflows/keepalive.yml` (ping a `/health` cada 12 min) + **resiliencia
  en `frontend/lib/api.ts`** (timeout 90 s, reintentos en cold start, mensaje
  "activando el servidor").

## Lenguaje "vista previa para evaluación"
- `Limpieza de lenguaje`: se elimina el de **"demo interna"**. El banner pasa a
  *"Vista previa — entorno de evaluación. No utilizar con datos reales de clientes
  sin la aprobación previa de Compliance"*; el header `X-Prototype-Notice` pasa a
  valer *"Evaluation environment - Do not use with real customer data"*; el log JSON
  usa `environment="evaluation"`; el PDF dice *"Vista previa para evaluación"*. El
  login **ya no muestra credenciales demo** y el seed **ya no imprime contraseñas**.

## Roles y umbrales QA
- `Roles admin/jefe/asesor`: tres roles — `admin` y `jefe` con los **mismos
  permisos** por ahora (gestión + analítica global, helper `is_manager`); `asesor`
  solo ve **su propio rendimiento**. `User.role` + `User.agent_id` (FK a agents);
  dependencia `require_manager`; `POST /agents/{id}/login` crea el login del asesor
  y vincula User↔Agent. Frontend: navegación/redirección por rol (asesor → `/mi-panel`,
  admin/jefe → `/dashboard`), guard por rol y página "Mi rendimiento". Migración
  `0005` (`users.agent_id` FK + backfill `'supervisor'`→`'jefe'`).
- `Umbrales QA configurables` en `/config/settings` (`qa_target_score=90`,
  `qa_low_agent_threshold=80`, `qa_red_call_threshold=60`, `qa_min_calls_ranking=5`,
  `qa_trend_drop_alert=5`), persistidos en `app_settings`, editables solo por manager.

## Rebrand a la identidad Minsait
- `Rebrand Minsait`: UI rebrandeada a la identidad oficial **Minsait** — paleta
  **Pruno `#480E2A`** + **Gris Cerámica `#E3E2DA`** dominantes, **Fucsia `#FF0054`**
  solo como acento; tipografía **ForFuture Sans** (woff2 locales), logo oficial,
  contenedores **achaflanados** (`.chamfer`), titulares en minúscula con la palabra
  clave en Fucsia, CTA en píldora, modo claro por defecto + sidebar siempre Pruno.
  Tokens en `frontend/app/globals.css` + `tailwind.config.ts`. **Sustituye** a
  "Aetheric Intelligence" / Índigo/Slate (obsoletos).

## Campañas con nota de producto
- `Campañas`: entidad `Campaign` (tabla `campaigns`) con una **nota de producto de
  9 campos** (producto/servicio, descripción de la oferta, beneficios, precio/condiciones,
  requisitos, frases obligatorias, claims prohibidos, público objetivo, notas). Se crea
  por formulario (con asistente IA) o subiendo un **PDF** que la IA parsea (pypdf + LLM)
  y autocompleta. La nota se **inyecta en el prompt de análisis** para evaluar si el
  ejecutivo ofreció la oferta correcta. `calls.campaign_id` (se conserva `campaign_type`
  por compatibilidad y filtros). Endpoints `/campaigns` CRUD + `/campaigns/extract` (PDF)
  + `/campaigns/assist` (IA). Dependencia nueva backend: **pypdf**. Módulo frontend
  `/campaigns`. Migración `0004` (tabla `campaigns` + `calls.campaign_id` + backfill).

## Despliegue en producción (gratis)
- **Publicado** en Vercel (frontend) + Render (backend + PostgreSQL), coste **$0**.
  Frontend: https://callqa-ai.vercel.app · Backend: https://callqa-api.onrender.com
- `Fix deploy Render`: el arranque (migraciones + seed + uvicorn) se movió al **CMD del
  Dockerfile** para evitar que Render partiera mal el comando con comillas (exit 127). (`53ee2d3`)
- `Despliegue gratis`: **procesamiento inline** (`PROCESS_INLINE`, vía `BackgroundTasks`)
  para correr **sin Celery/Redis** en el tier gratis; `render.yaml` (blueprint Render con
  PostgreSQL); normaliza `postgres://`→`postgresql://`; `DEPLOY_GRATIS.md`. (`8523b01`)

## Auditoría de consistencia
- `Consolidación de docs`: **toda la documentación se movió a `docs/`**; en la raíz solo
  quedan `README.md` y los punteros `AGENTS.md` / `CLAUDE.md`. (`2d10ab1`)
- `AGENTS/CHANGELOG/docs`: guía canónica `AGENTS.md`, este changelog y sincronización
  de la documentación de origen. (`d43940c`)
- `Docs sync`: toda la documentación a la realidad **"Groq por defecto"** (proveedor IA,
  costos $0, diarización por LLM, colores Índigo/Slate, rúbrica editable, tests). (`59152cf`)
- `Fixes funcionales/config`: `/config/settings` reporta el **proveedor REAL** (env, no BD);
  defaults a `groq`; `dimensionLabel` humaniza categorías nuevas. (`f077825`)

## Funcionalidades
- `Filtros del dashboard` (campaña, ejecutivo, rango de fechas, periodo) + endpoint
  `/dashboard/campaigns`. **Rediseño de paleta a Índigo/Slate** (en `globals.css`). (`c518519`)
- `Rúbrica con subcategorías`: activables + **añadir/eliminar categorías y subcategorías**;
  la IA las usa (prompt dinámico). Migración `0003` (`rubric_config.criteria`). (`d184f3c`)
- `Diarización por contenido (LLM)` en vez de la heurística de pausas (que queda de fallback);
  `max_tokens` 4000. (`21319bb`)
- `Botón Actualizar` en listado y detalle de llamadas. (`9a76dbf`)

## Correcciones
- `Dashboard 500` ("Network Error"): comparación de fechas naïve/aware → `datetime.utcnow()`. (`9a76dbf`)
- `Reintento idempotente`: `_run_pipeline` borra transcripción/análisis previos (evita
  `IntegrityError UNIQUE(call_id)`); `db.rollback()` antes de marcar `ERROR`. (`c61c3fb`)
- `Enmascarado endurecido`: cubre tarjetas con guiones/espacios y números dictados
  (best-effort, documentado). Claims de seguridad del README ejecutivo hechos honestos. (`c61c3fb`)

## Base
- `Initial commit`: backend FastAPI + Celery, frontend Next.js, docs. (`134b42c`)
