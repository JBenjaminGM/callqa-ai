# AGENTS.md — Guía para IAs y desarrolladores

> **Lee esto primero.** Es el punto de entrada para entender el proyecto y hacer
> cambios sin contexto previo. Es la **fuente de verdad del estado ACTUAL**; los
> documentos de `docs/` son la especificación de origen (algunos ya históricos).

---

## 1. Qué es

**CallQA AI**: plataforma web de **Quality Assurance automatizado con IA** para
call centers bancarios. Un supervisor sube audios de llamadas; la IA las
transcribe, las analiza contra una **rúbrica configurable** y devuelve scores por
dimensión, un score global tipo NPS, recomendaciones y comparativas.

> ⚠️ Es un **prototipo / PoC interno** de Minsait (Grupo Indra). No usar con datos
> reales de clientes sin aprobación de Compliance/DPO.

## 2. Estado actual (en vivo)

- **Repo:** `github.com/JBenjaminGM/callqa-ai` (rama `main`). **Push a `main` ⇒ redeploy automático** en Vercel y Render.
- **Frontend (Vercel):** https://callqa-ai.vercel.app
- **Backend (Render):** https://callqa-api.onrender.com (`/health`, `/docs`)
- **Login demo:** `admin@callqa.com` / `Admin123!`
- **Coste de operación: $0** (Groq gratis + tiers gratis de Vercel/Render).
- **Ubicación de trabajo local:** `C:\Users\Benja\Documents\callqa-ai` (NO la copia de OneDrive — Docker falla desde OneDrive por archivos "solo en la nube").

## 3. Arquitectura

```
Navegador ─HTTPS→ Frontend (Next.js·Vercel) ─REST→ Backend (FastAPI·Render)
                                                       ├─→ PostgreSQL (Render)
                                                       └─→ Groq (Whisper + Llama)
```

- **En la nube** el backend procesa la llamada **dentro de la propia API**
  (`PROCESS_INLINE=true`, vía `BackgroundTasks`) — **sin Celery/Redis**, para caber
  en el tier gratis de Render (no ofrece workers).
- **En local (`docker-compose`)** se usa el modo "producción" con **Celery + Redis**
  (un worker procesa las tareas). `PROCESS_INLINE` queda en `false`.
- **GitHub** dispara los despliegues. **No hay CI propio**; Vercel/Render construyen al hacer push.

## 4. Stack

| Capa | Tecnologías |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, TanStack Query, Zustand, Recharts, Axios, Zod (react-hook-form) |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, slowapi |
| Cola (solo local) | Celery 5 + Redis |
| Base de datos | PostgreSQL 15 |
| IA — transcripción | **Groq** · Whisper large v3 |
| IA — análisis | **Groq** · Llama 3.3 70B (`AI_PROVIDER=groq`) · factory → claude / openai / azure |
| Seguridad | JWT (python-jose), bcrypt (passlib), CORS lista blanca |
| Infra | Docker, GitHub, Vercel (frontend), Render (backend+PostgreSQL) |

## 5. Mapa del repositorio (dónde está cada cosa)

```
backend/
  app/
    main.py            App FastAPI: CORS, logging JSON, routers, /health, header de prototipo
    config.py          Settings desde env. ai_provider=groq (default), process_inline,
                       y normaliza postgres:// → postgresql:// (Render/Heroku)
    database.py        engine + SessionLocal + get_db()
    dependencies.py    get_current_user (valida el JWT)
    models/            SQLAlchemy: user, agent, call, transcription, analysis,
                       settings.py (RubricConfig con `criteria` JSON, + AppSettings)
    schemas/           DTOs Pydantic: auth, agent, call, analysis, dashboard, config
    routers/           auth, agents, calls, dashboard, config
    services/          analysis_service.py  → factory IA (ClaudeProvider/OpenAIProvider/
                                               GroqLLMProvider(=OpenAI compatible)/Azure) + calculate_global_score
                       transcription_service.py → factory STT (Groq/local/azure) +
                                               add_speaker_diarization (heurística de FALLBACK)
                       masking_service.py    → enmascarado best-effort (regex)
                       name_matching.py      → matching difuso de nombres de ejecutivo
                       call_service.py, agent_service.py, auth_service.py,
                       storage_service.py (local/s3), pdf_service.py
    tasks/
      call_tasks.py    process_call + _run_pipeline (EL pipeline; ver §6)
      celery_app.py    config de Celery (solo se usa en modo no-inline)
    prompts/
      __init__.py      get_analysis_prompt(segments, rubric, language)
      analysis_es.py / analysis_en.py  → prompt DINÁMICO: lista subcriterios activos y
                       genera la estructura "dimension_scores" con las claves reales de la rúbrica
    utils/             security.py (JWT/bcrypt), audio.py (validación de archivos)
  alembic/versions/    0001 esquema, 0002 detección ejecutivo, 0003 rubric_config.criteria
  scripts/seed_data.py admin + rúbrica (7 dims con subcriterios) + settings + 3 ejecutivos demo
  tests/               33 tests (conftest = SQLite en memoria, todo lo externo mockeado)
  Dockerfile           multi-stage. CMD = alembic upgrade + seed + uvicorn (lo usa Render)
  .env / .env.example  (.env está gitignorado)
frontend/
  app/                 App Router: login/, (main)/{dashboard, calls, calls/new, calls/[id],
                       agents, agents/[id], settings}, layout, providers
  components/          ui/ (button, input, card, badge, select, feedback…), layout/, charts/, dashboard/
  lib/                 api.ts (axios + interceptores 401), auth.ts (Zustand + JWT en localStorage),
                       queries.ts (TODOS los hooks de TanStack Query), utils.ts (dimensionLabel, formatos)
  types/index.ts       Tipos TS que reflejan la API
  app/globals.css      ★ COLORES CANÓNICOS (variables CSS Índigo/Slate, modo claro+oscuro)
  tailwind.config.ts   mapea los colores a las variables CSS
docs/                  00–07 + DESIGN.md (especificación de origen; ver §9)
docker-compose.yml     stack local completo (postgres, redis, api, worker, frontend)
render.yaml            blueprint de Render (backend Docker + PostgreSQL, PROCESS_INLINE=true)
DEPLOY_GRATIS.md       guía de despliegue gratis (Vercel + Render)
CHANGELOG.md           historial de cambios
```

## 6. El pipeline de análisis (`backend/app/tasks/call_tasks.py`)

`process_call(call_id)` → `_run_pipeline`:
1. **Idempotencia:** borra transcripción/análisis previos (permite reintentar sin violar `UNIQUE(call_id)`).
2. **Transcribe** el audio con el proveedor STT (Groq Whisper) → texto + segmentos.
3. **Diarización heurística de FALLBACK** (`add_speaker_diarization`, por pausas).
4. Guarda la **transcripción**.
5. **Enmascara** datos sensibles de cada segmento (best-effort).
6. Lee la **rúbrica** (con subcriterios) y construye el **prompt dinámico**.
7. **LLM** (Groq Llama) → `dimension_scores`, `summary`, `recommendations`, `detected_agent_name` y `diarization`.
8. **Aplica la diarización del LLM** (por contenido) sobre los segmentos (corrige la heurística).
9. **calcula el score global** ponderado; **detecta+empareja** al ejecutivo (matching difuso).
10. Guarda el **análisis** → estado `DONE`.
- Si algo falla: `db.rollback()` y marca `ERROR` con el detalle.

## 7. Cómo correr y testear (local, Windows sin admin)

- **Stack completo (Docker):** `cd C:\Users\Benja\Documents\callqa-ai && docker compose up -d --build`
  → app http://localhost:3000 · API http://localhost:8000/docs · login `admin@callqa.com`/`Admin123!`.
  Apagar: `docker compose down`.
- **Tests backend (33):** desde `backend/`, `.\.venv\Scripts\python.exe -m pytest -q`
  (el venv ya tiene `requirements.txt`; SQLite en memoria, sin red).
- **Build frontend:** desde `frontend/`, `npm run build`.
- **Herramientas:** Python 3.11 (user install), Node v24 portátil (`%LOCALAPPDATA%\node-portable\...`), Docker Desktop. La consola es cp1252 → al ejecutar Python con Unicode usar `$env:PYTHONIOENCODING="utf-8"`.

## 8. Variables de entorno clave (`backend/.env`)

| Variable | Valor | Nota |
|---|---|---|
| `GROQ_API_KEY` | `gsk_...` | Transcripción **y** análisis (gratis) |
| `AI_PROVIDER` | `groq` | factory: `groq` \| `claude` \| `openai` \| `azure` |
| `AI_MODEL_GROQ` | `llama-3.3-70b-versatile` | |
| `WHISPER_PROVIDER` | `groq` | |
| `PROCESS_INLINE` | `false` local / `true` en Render | Sin worker Celery cuando es `true` |
| `DATABASE_URL` | postgres… | Se normaliza `postgres://`→`postgresql://` |
| `JWT_SECRET` | cadena larga | Cambiar en producción |
| `CORS_ORIGINS` | URL(s) del frontend | Lista blanca separada por comas |

## 9. Decisiones clave y *gotchas* (LÉELO antes de tocar)

- **IA = Groq por defecto.** Para usar Claude/OpenAI/Azure: cambiar `AI_PROVIDER` + poner su API key. El código YA lo soporta (factory en `analysis_service.py`). Portar a **Azure OpenAI + Azure AI Speech** (producción Indra) = solo configuración.
- **`/config/settings` reporta el proveedor REAL** (de la env var), no el de la BD — para que la UI no mienta.
- **Enmascarado = best-effort**, NO garantía. Los regex cazan dígitos/algunos números dictados, pero **el audio crudo sale a Groq (EE. UU.)**. Para datos reales: transcripción on-prem/Azure + DPO/CISO.
- **Diarización (quién habla):** la hace el **LLM por contenido**; la heurística de pausas es solo fallback. Es aproximada en turnos ambiguos. Fiable de verdad = speaker-ID acústico (Azure Speech / pyannote).
- **Rúbrica DINÁMICA:** editable con subcriterios activables y **categorías que se pueden añadir/eliminar**. `PUT /config/rubric` es **reemplazo completo** (crea/actualiza/borra; genera la clave con slug). El prompt construye `dimension_scores` con las claves reales → las categorías nuevas se puntúan solas. En el frontend, `dimensionLabel()` (lib/utils.ts) humaniza claves desconocidas.
- **Dashboard:** filtros campaña/ejecutivo/fechas/periodo; endpoint `/dashboard/campaigns`. Las fechas se comparan con `datetime.utcnow()` (naïve) porque la BD guarda timestamps naïve — NO usar `datetime.now(timezone.utc)` ahí (rompía con un `TypeError`).
- **Colores:** la fuente de verdad es `frontend/app/globals.css` (variables CSS Índigo/Slate). `docs/DESIGN.md` es referencia; **`docs/07_DISEÑO_VISUAL.md` está OBSOLETO**.
- **Despliegue:** el arranque (migraciones+seed+uvicorn) vive en el **CMD del Dockerfile** (no en `render.yaml`) para evitar que Render parta mal el comando con comillas (daba exit 127).

## 10. Cómo hacer cambios comunes

- **Añadir un endpoint:** crea/edita en `app/routers/`, regístralo en `app/main.py`, añade su schema en `app/schemas/` y, si toca BD, su modelo + migración Alembic.
- **Cambiar la BD:** edita el modelo en `app/models/`, luego `alembic revision -m "..."` (o crea el archivo a mano siguiendo `0003`), y `alembic upgrade head`. El `seed_data.py` corre en cada arranque (idempotente).
- **Cambiar/añadir proveedor IA:** `app/services/analysis_service.py` (análisis) o `transcription_service.py` (STT) — patrón factory. Variable `AI_PROVIDER`/`WHISPER_PROVIDER`.
- **Tocar el prompt de la IA:** `app/prompts/analysis_es.py` / `_en.py` (es dinámico según la rúbrica).
- **Cambiar colores/diseño:** `frontend/app/globals.css` (variables) — se propaga a toda la app y a los gráficos.
- **Añadir una página/hook frontend:** página en `frontend/app/(main)/...`, hooks de datos en `frontend/lib/queries.ts`, tipos en `frontend/types/index.ts`.
- **Desplegar cambios:** solo `git push origin main` (Vercel + Render redepliegan).

## 11. Tests

33 tests en `backend/tests/` (pytest, SQLite en memoria, externos mockeados). Cubren auth, agentes, score, enmascarado, matching difuso, subida, **idempotencia del reintento** y **modo inline**. **No** cubren el end-to-end real con APIs (eso se valida con audios reales). Correr antes de cada cambio.

## 12. Mapa de documentación

| Archivo | Qué es | Vigencia |
|---|---|---|
| **AGENTS.md** (este) | Estado actual + cómo trabajar | ✅ canónico |
| **CHANGELOG.md** | Historial de cambios | ✅ |
| **README.md** | Arranque rápido | ✅ |
| **DEPLOY_GRATIS.md** | Despliegue Vercel+Render gratis | ✅ |
| **ESTADO_DEL_PROYECTO.md** | Memoria del proyecto | ✅ (ver AGENTS.md para lo más nuevo) |
| `docs/01,02,03` | Visión, requerimientos, arquitectura | ✅ mayormente (sincronizados a Groq) |
| `docs/06_README_EJECUTIVO.md` | Pitch ejecutivo | ✅ |
| `docs/DESIGN.md` | Sistema de diseño | ✅ (paleta Índigo/Slate) |
| `docs/04_PROMPT_BACKEND.md`, `docs/05_GUIA_DESPLIEGUE.md` | Prompt de generación / guía vieja | ⚠️ históricos (con banner) |
| `docs/07_DISEÑO_VISUAL.md` | Paleta antigua | ❌ OBSOLETO |
