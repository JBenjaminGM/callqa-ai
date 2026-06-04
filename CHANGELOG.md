# Changelog — CallQA AI

Cambios relevantes. Formato: descripción (commit). Lo más nuevo arriba.

## Despliegue en producción (gratis)
- **Publicado** en Vercel (frontend) + Render (backend + PostgreSQL), coste **$0**.
  Frontend: https://callqa-ai.vercel.app · Backend: https://callqa-api.onrender.com
- `Fix deploy Render`: el arranque (migraciones + seed + uvicorn) se movió al **CMD del
  Dockerfile** para evitar que Render partiera mal el comando con comillas (exit 127). (`53ee2d3`)
- `Despliegue gratis`: **procesamiento inline** (`PROCESS_INLINE`, vía `BackgroundTasks`)
  para correr **sin Celery/Redis** en el tier gratis; `render.yaml` (blueprint Render con
  PostgreSQL); normaliza `postgres://`→`postgresql://`; `DEPLOY_GRATIS.md`. (`8523b01`)

## Auditoría de consistencia
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
