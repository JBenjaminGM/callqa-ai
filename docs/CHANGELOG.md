# Changelog — CallAIbrate

Cambios relevantes. Formato: descripción (commit). Lo más nuevo arriba.

> Las entradas anteriores al rebrand se conservan tal cual: nombran el producto como
> "CallQA AI" y la identidad Minsait porque así era entonces. Son historia, no estado.

## Rebrand a CallAIbrate + reproductor, export CSV y seguridad
- `Marca`: nueva identidad **CallAIbrate** con `docs/BRAND.md` como fuente de verdad.
  Paleta **paper `#F5F1E8`** / **ink `#2A2420`** con acentos **rust `#B8441F`** y
  **gold `#A67C27`**; tipografías **Manrope / Inter / IBM Plex Mono** vía
  `next/font/google` (esta última **solo** para datos numéricos). Se retiran la paleta
  Minsait, ForFuture Sans y los logos corporativos; `frontend/public/fonts` y
  `public/brand` se **eliminan** (además, las woff2 eran tipografía con licencia).
- `Formas`: la clase `.chamfer` (chaflán octogonal) se sustituye por radios de **8 px**
  en contenedores (`rounded-card`) y **6 px** en controles (`rounded-control`). Los
  círculos (avatares, puntos de estado, barras de progreso) se conservan.
- `Wordmark`: `frontend/components/brand/logo.tsx` exporta `<Waveform />` y
  `<Wordmark />` como SVG real; el fragmento "AI" siempre en rust. Nuevo `favicon.svg`.
- `Copy`: titulares en caso frase (se retira `text-transform: lowercase`), conservando
  el resalte `.hl` de una palabra clave, ahora en rust.
- `Modo oscuro`: se mantiene, con paleta derivada documentada en el addendum de `BRAND.md`.
- `Reproductor de audio sincronizado`: nuevo `GET /api/v1/calls/{id}/audio` (con el
  mismo control de acceso que el detalle, y 404 explicativo si el almacenamiento perdió
  el archivo) y `components/calls/transcript-player.tsx`, que resalta el segmento que
  suena y salta al hacer clic. El audio se descarga como blob porque `<audio src>` no
  puede enviar la cabecera `Authorization`.
- `Exportación CSV`: nuevo `GET /api/v1/dashboard/report.csv` (solo admin/jefe), una
  fila por ejecutivo con las 7 dimensiones, BOM UTF-8 para Excel, y botón en el
  dashboard que respeta los filtros activos.
- `Seguridad`: el seed **genera contraseñas aleatorias** (fijables con
  `SEED_ADMIN_PASSWORD` / `SEED_JEFE_PASSWORD` / `SEED_ASESOR_PASSWORD`), las imprime
  una sola vez, migra los emails `@callqa.com` a `@callaibrate.com` conservando la
  cuenta, y **rota** cualquier cuenta sembrada que aún use una de las contraseñas que
  llegaron a estar publicadas en el repo. Se retiran las credenciales literales de
  README y docs.
- `Seguridad`: guardarraíl que **aborta el arranque** si `APP_ENV=production` con el
  `JWT_SECRET` de ejemplo.
- `Corrección`: `datetime.utcnow()` (obsoleto) sustituido por un helper explícito en
  `dashboard_service.py` que devuelve UTC *naive*, para poder comparar con las columnas
  `DateTime` sin zona horaria.
- `Docs`: `BRAND.md` y `COMPLIANCE_CHECKLIST.md` nuevos; `DESIGN.md` reescrito;
  `CallQA_AI_Presentacion.pptx` eliminado (marca antigua + credenciales demo dentro).
- `Tests`: 78 → **87** (audio: 200/404/403; CSV: contenido, filtro de campaña y 403 de
  asesor; guardarraíl de `JWT_SECRET`).

## Auditoría de coherencia y limpieza
- `Código muerto eliminado`: componente `kpi-card.tsx` (sustituido por `StatCard`),
  factory `require_role` sin uso, fixture `seed_rubric`, campo `estimated_completion_seconds`,
  y los settings `ai_provider`/`whisper_provider` que se persistían en BD pero **nunca se
  leían** (el proveedor lo fija la env var). Artefactos legacy de Railway (`railway.json`,
  `Procfile`).
- `Comentarios/docstrings alineados al estado real`: Railway→Render, "MVP"→"por defecto",
  3→4 proveedores de IA, Celery→dual (inline), NPS→ranking, `environment="evaluation"`,
  y limpieza de estética obsoleta en el frontend (Aetheric/Índigo/"immersive"/`backdrop-blur`
  muerto sobre superficies sólidas). Color del PDF `#E84F7A`→Pruno `#480e2a`.
- `Docs consolidados`: se eliminaron los specs de origen numerados (01–07); su contenido
  útil (casos de uso, reglas de negocio, gobernanza/compliance) se consolidó en
  `ESTADO_DEL_PROYECTO.md`. `docs/` queda mínimo y coherente.
- `Migración 0007`: `server_default` de `users.role` corregido de `'supervisor'` (legacy) a `'jefe'`.
- `.env.example` completado (`PROCESS_INLINE`, CORS, id de modelo Claude) y `.env.local.example`
  apuntando a Render.

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
