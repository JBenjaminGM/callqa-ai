# 🧠 Estado del Proyecto — CallQA AI

> **Memoria de desarrollo.** Este documento resume lo construido, las decisiones y lo pendiente.
>
> 👉 **Para el estado MÁS ACTUAL y la guía de desarrollo** (cómo correr, testear, desplegar y
> dónde tocar cada cosa), ver **[`AGENTS.md`](AGENTS.md)** y **[`CHANGELOG.md`](CHANGELOG.md)**.

**Última actualización:** Junio 2026
**Estado general:** ✅ MVP funcional **desplegado en producción gratis** (Vercel + Render),
con transcripción y análisis vía **Groq** (coste $0). 61 tests backend en verde.

---

## 1. ¿Qué es CallQA AI?

Plataforma web de **Quality Assurance automatizado con IA** para call centers
bancarios. El usuario sube grabaciones de llamadas; la IA las transcribe
(Groq Whisper large v3), **enmascara la PII** (best-effort), identifica al
ejecutivo y las **evalúa** con un LLM (Groq Llama 3.3 70B) contra una rúbrica
dinámica, produciendo scores por dimensión, un score global ponderado,
recomendaciones accionables y un reporte PDF. Cliente: Minsait (Grupo Indra),
sector banca.

> ⚠️ Es una **vista previa para evaluación** que se presenta oficialmente al
> cliente; sigue siendo un prototipo. No debe usarse con datos reales de clientes
> sin la aprobación previa de Compliance. Todas las pantallas muestran un banner:
> *"Vista previa — entorno de evaluación. No utilizar con datos reales de clientes
> sin la aprobación previa de Compliance"*.

---

## 2. Arquitectura y stack

```
Navegador ──HTTPS──> Frontend (Next.js 14) ──REST──> Backend (FastAPI)
                                                         │
                                  ┌──────────────────────┼───────────────┐
                                  ▼              ▼                ▼
                            PostgreSQL        Redis          Celery worker
                                                              │   │
                                                       Groq ◄─┘   └─► Groq (LLM)
                                                    (Whisper)     (análisis · Claude/GPT opc.)
```

> En Render (producción gratis) **no hay Celery/Redis**: el procesamiento es
> **inline** vía `BackgroundTasks` (`PROCESS_INLINE=true`).

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, slowapi |
| Seguridad / auth | python-jose + passlib (JWT + bcrypt) |
| HTTP / PDF | httpx · reportlab (genera PDF) · pypdf (lee PDF) · boto3 (S3 opcional) |
| Procesamiento asíncrono | Celery 5 + Redis (local) · inline con `BackgroundTasks` (Render) |
| Base de datos | PostgreSQL 15 |
| IA — transcripción | Groq API (Whisper large v3) |
| IA — análisis | Groq (Llama 3.3 70B, gratis) · factory portable a Claude / OpenAI / Azure |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Datos en frontend | TanStack Query + Axios; estado de sesión con Zustand |
| Gráficos | Recharts |
| Tipografía | ForFuture Sans (woff2 locales) |
| Contenedores | Docker Compose (todo el stack) |

---

## 3. Estructura del monorepo

```
callqa-ai/
├── docker-compose.yml        # Levanta TODO el stack local: bd + redis + api + worker + frontend
├── render.yaml               # Blueprint de Render (backend Docker + PostgreSQL)
├── README.md                 # Guía rápida del monorepo
├── AGENTS.md / CLAUDE.md      # Punteros que apuntan a docs/AGENTS.md
│
├── .github/workflows/
│   └── keepalive.yml         # Ping a /health cada 12 min (mitiga el cold-start de Render)
│
├── backend/                  # API FastAPI + worker Celery
│   ├── app/
│   │   ├── main.py            # Arranque, CORS, logging JSON, routers
│   │   ├── config.py          # Configuración por variables de entorno
│   │   ├── models/            # Tablas SQLAlchemy
│   │   ├── schemas/           # DTOs Pydantic
│   │   ├── routers/           # Endpoints REST
│   │   ├── services/          # Lógica de negocio (IA, storage, matching, PDF, PDF de campañas)
│   │   ├── tasks/             # Tareas Celery
│   │   └── prompts/           # Prompts para los LLM
│   ├── alembic/               # Migraciones de BD (0001 … 0005)
│   ├── scripts/seed_data.py   # Datos iniciales (no imprime contraseñas)
│   ├── tests/                 # 61 tests automatizados
│   └── docker-compose.yml     # Compose SOLO del backend (para devs)
│
├── frontend/                 # Aplicación Next.js
│   ├── app/                   # Páginas (login + grupo (main) + /campaigns + /mi-panel)
│   │   └── globals.css        # Tokens de color Minsait (fuente de verdad)
│   ├── components/            # UI, layout, charts, dashboard
│   ├── lib/
│   │   └── api.ts             # Axios + resiliencia de cold-start (timeout 90s, reintentos)
│   ├── public/fonts/          # ForFuture Sans (woff2)
│   ├── public/brand/          # Logo oficial Minsait
│   ├── types/                 # Tipos TypeScript
│   ├── tailwind.config.ts     # Tokens de color Minsait
│   └── Dockerfile             # Imagen de producción (salida standalone)
│
└── docs/                     # TODA la documentación del proyecto
    ├── AGENTS.md              # Guía canónica de desarrollo (la más importante)
    ├── 00_INDICE.md           # Índice de la documentación
    ├── ESTADO_DEL_PROYECTO.md # Este archivo (memoria del proyecto)
    └── CHANGELOG.md · DEPLOY_GRATIS.md
```

---

## 4. Funcionalidades implementadas

### Backend

- **Autenticación** JWT (login, refresh, logout, me) con rate limiting en login
  (5 intentos / 15 min). `me` devuelve `role` y `agent_id`.
- **Roles y scoping**: tres roles — `admin`, `jefe` (mismos permisos por ahora,
  vía helper `is_manager`) y `asesor` (solo ve su propio rendimiento). La
  dependencia `require_manager` protege los endpoints de gestión.
- **Ejecutivos** (agents): alta, edición, baja lógica, estadísticas y
  **creación del login del asesor** (`POST /agents/{id}/login`, vincula User↔Agent).
- **Campañas con nota de producto**: entidad `Campaign` con una nota de producto
  de 9 campos; se crea por formulario (con asistente IA), o subiendo un **PDF**
  que la IA parsea (pypdf + LLM) y autocompleta. La nota se **inyecta en el
  prompt de análisis** para evaluar si el ejecutivo ofreció la oferta correcta.
- **Llamadas**: subida individual y **en lote**, listado paginado con filtros
  (ejecutivo, estado, **rango de fechas**, campaña), detalle, estado para
  polling, asignación, reintento (idempotente), reporte PDF, borrado.
- **Procesamiento** (`QUEUED → TRANSCRIBING → ANALYZING → DONE`): Celery en
  local; **inline** (`BackgroundTasks`) en Render.
- **Dashboard**: KPIs del equipo, distribución de scores, rankings, performance
  por ejecutivo, con filtros (campaña, ejecutivo, fechas, periodo).
- **Configuración**: rúbrica **editable** (dimensiones por defecto, con
  subcategorías activables y posibilidad de añadir/eliminar categorías; la IA
  usa las subcategorías activas), idioma de análisis y **umbrales QA**
  configurables (objetivo, alerta de asesor, llamada roja, mínimo de llamadas
  para ranking, alerta de caída de tendencia).
- **Seguridad**: enmascarado best-effort de datos sensibles (tarjetas, DNI, CVV)
  antes de enviar texto a la IA; contraseñas con bcrypt; CORS por lista blanca.
- **Patrón factory** para proveedores de IA y transcripción → portable a
  Claude / OpenAI / Azure (solo configuración).

### Frontend

- Login (sin credenciales demo a la vista), dashboard, listado/subida/detalle de
  llamadas, ejecutivos, **campañas** (lista, crear vía PDF/IA/formulario, editar),
  configuración y **Mi rendimiento** (panel del asesor).
- **Navegación y redirección por rol**: asesor → `/mi-panel`; admin/jefe →
  `/dashboard`; guard por rol que devuelve 403 a quien no corresponde.
- Identidad visual **Minsait** (modo claro por defecto, sidebar Pruno).
- Banner de **vista previa para evaluación** en todas las pantallas.
- Polling automático del estado de las llamadas en proceso.
- **Resiliencia de cold-start** en `lib/api.ts` (timeout 90 s, reintentos,
  mensaje "activando el servidor").
- Gráficos: distribución de scores, radar por dimensión, evolución temporal.

---

## 5. Flujo de trabajo (versión actual)

1. Un manager (admin/jefe) sube **un grupo de audios MP3**. Solo indica: los
   archivos, la **campaña**, un **comentario opcional** y el **responsable** de
   la subida. No elige ejecutivo.
2. Por cada llamada, la IA transcribe el audio, **enmascara la PII** y **detecta
   el nombre del ejecutivo** (siempre se presenta al inicio de la llamada).
3. El nombre detectado se compara (**matching difuso**, tolera erratas como
   "Juan Perz" → "Juan Pérez") con los ejecutivos registrados:
   - **Coincide** → la llamada se asigna a ese ejecutivo.
   - **No coincide** → la llamada queda con el nombre detectado y la etiqueta
     "Sin registrar".
4. La IA **evalúa** la llamada contra la rúbrica dinámica, inyectando la **nota
   de producto** de la campaña para comprobar si se ofreció la oferta correcta.
5. El manager puede **crear** después al ejecutivo no registrado; al crearlo, sus
   llamadas previas se le **vinculan automáticamente**. También puede asignar
   manualmente desde el detalle de cada llamada.
6. El manager consulta el **dashboard** y el detalle individual de cada
   llamada/ejecutivo. El **asesor** entra a su panel **"Mi rendimiento"** y solo
   ve su ficha y sus propias llamadas.

---

## 6. Sistema de diseño

Identidad visual oficial **Minsait** (Grupo Indra):

- Paleta corporativa: **Pruno `#480E2A`** y **Gris Cerámica `#E3E2DA`** dominan;
  **Fucsia `#FF0054`** únicamente como **acento** (CTA en píldora, palabra clave
  de los titulares).
- **Modo claro por defecto** (Gris Cerámica) + **modo oscuro Pruno**.
- **Sidebar siempre Pruno** con el logo oficial Minsait en blanco.
- Contenedores **achaflanados** (clase `.chamfer`).
- Titulares en minúscula con la palabra clave en Fucsia (dispositivo
  "calidad con impacto").
- Tipografía **ForFuture Sans** (woff2 locales en `frontend/public/fonts`).
- **Fuente de verdad del color:** `frontend/app/globals.css` + `tailwind.config.ts`.

> Nota histórica: iteraciones previas usaron la paleta corporativa púrpura de
> Minsait, una paleta Electric Rose / Deep Plum y, más tarde, el sistema
> "Aetheric Intelligence" con paleta Índigo/Slate; **todas quedaron obsoletas**
> al adoptar la identidad oficial Minsait actual.

---

## 7. Modelo de datos (resumen)

| Tabla | Contenido |
|---|---|
| `users` | Cuentas de login (`role` admin/jefe/asesor, `agent_id` opcional, `last_login`) |
| `agents` | Ejecutivos evaluados (`name`, `email`, `campaign`, `active`…) |
| `campaigns` | Campaña con nota de producto (9 campos) + `source` + `active` |
| `calls` | Llamadas subidas; `agent_id` nullable; `uploaded_by`, `campaign_id`, `campaign_type`, `detected_agent_name`, `responsible`, `status` |
| `transcriptions` | Transcripción + segmentos con timestamps (1:1 con call) |
| `analyses` | Scores por dimensión, score global, recomendaciones, resumen (1:1 con call) |
| `rubric_config` | Rúbrica editable: dimensiones con pesos y subcategorías activables (`criteria` JSON) |
| `app_settings` | Configuración global (idioma + umbrales QA `qa_*`) |

Migraciones (Alembic):

- **0001** esquema inicial.
- **0002** detección de ejecutivo (`agent_id` nullable + `detected_agent_name` + `responsible`).
- **0003** rúbrica con subcriterios (`rubric_config.criteria` JSON).
- **0004** campañas (tabla `campaigns` + `calls.campaign_id` + backfill de campañas existentes).
- **0005** roles de usuario (`users.agent_id` FK + backfill `'supervisor'` → `'jefe'`).

---

## 8. Cómo ejecutarlo

Requisito: **Docker Desktop** abierto.

```bash
cd callqa-ai
docker compose up -d --build
```

Levanta 5 servicios (postgres, redis, api, worker, frontend).

- Frontend: <http://localhost:3000>
- API / docs: <http://localhost:8000/docs>
- Cuentas sembradas: `admin@callqa.com` / `Admin123!` (admin) ·
  `jefe@callqa.com` / `Jefe123!` (jefe) · un **asesor** por cada ejecutivo demo
  (su email, p. ej. `maria@banco.com` / `Asesor123!`).

Tests backend (desde `backend/`): `.\.venv\Scripts\python.exe -m pytest -q`.
Build frontend (desde `frontend/`): `npm run build`.

Para detener: `docker compose down`.

### Para que el análisis con IA funcione

Por defecto basta una **clave de Groq** en `backend/.env` (hace transcripción **y**
análisis, gratis):

```
GROQ_API_KEY=gsk_...
AI_PROVIDER=groq
WHISPER_PROVIDER=groq
```

Sin ella, las llamadas subidas quedan en estado `ERROR` al transcribir.
Claude / OpenAI / Azure son opcionales: cambia `AI_PROVIDER` y pon su API key.

> 💡 También está **desplegado en vivo y gratis** (Vercel + Render); para publicarlo
> tú mismo, ver `DEPLOY_GRATIS.md`.

---

## 9. Despliegue en producción (gratis, coste $0)

- **Frontend** en Vercel: <https://callqa-ai.vercel.app>
  (necesita `NEXT_PUBLIC_API_URL=https://callqa-api.onrender.com/api/v1`).
- **Backend + PostgreSQL** en Render: <https://callqa-api.onrender.com>
  (necesita `GROQ_API_KEY`, `CORS_ORIGINS=https://callqa-ai.vercel.app`,
  `PROCESS_INLINE=true`, `JWT_SECRET`).
- Despliegue: `git push origin main` → Vercel y Render redepliegan solos.

**Cold-start.** El plan gratis de Render duerme el backend tras ~15 min de
inactividad; el arranque en frío (~50 s) puede verse como "error de API".
Mitigado con: GitHub Action `.github/workflows/keepalive.yml` (ping a `/health`
cada 12 min) + **resiliencia en `frontend/lib/api.ts`** (timeout 90 s, reintentos
en cold start, mensaje "activando el servidor"). El PostgreSQL gratis de Render
caduca a los **90 días**.

---

## 10. Verificaciones realizadas

| Verificación | Resultado |
|---|---|
| Build Docker del backend | ✅ |
| Tests del backend (`pytest`) | ✅ 61/61 |
| Migraciones 0001 … 0005 | ✅ aplican sin error |
| Build de producción del frontend | ✅ tipos TS válidos |
| Endpoints API (auth, agents, campaigns, calls, dashboard, config) | ✅ |
| Roles y scoping (admin / jefe / asesor) | ✅ (tests) |
| CORS frontend ↔ backend | ✅ |
| Subida en lote, filtro por fecha, asignación, auto-vínculo | ✅ |
| Campañas (CRUD, extracción de PDF, asistente IA) | ✅ |
| Matching difuso de nombres | ✅ (test unitario) |
| Reintento idempotente y modo inline | ✅ (tests) |

---

## 11. Pendientes / próximos pasos

- [x] **Despliegue en la nube** (frontend → Vercel, backend + PostgreSQL → Render),
      **gratis** y en vivo. Ver `DEPLOY_GRATIS.md`.
- [x] **Groq configurado** (`GROQ_API_KEY` real) haciendo transcripción y análisis
      en producción.
- [x] **Roles** admin/jefe/asesor con scoping y panel "Mi rendimiento".
- [x] **Campañas con nota de producto** (formulario / asistente IA / extracción de PDF).
- [x] **Umbrales QA** configurables y **cold-start** mitigado (keepalive + resiliencia).
- [ ] Analítica de jefe de alto impacto (alertas accionables, KPIs por campaña,
      top asesores y problemas recurrentes).
- [ ] Métricas de conversación (talk/listen ratio, % silencio, monólogos,
      velocidad de habla) derivadas de la transcripción.
- [ ] Vista de asesor enriquecida (percentil anónimo en la campaña, "qué cambiar"
      con evidencia, cumplimiento por campaña).
- [ ] Reproductor de audio sincronizado con la transcripción.
- [ ] Exportación masiva (CSV) del reporte del equipo.
- [ ] Antes de producción real: validaciones de Compliance, DPO y Seguridad.

---

## 12. Historial de iteraciones

1. **Generación inicial** del backend completo (FastAPI + Celery + modelo de
   datos + tests) a partir del prompt maestro de `04_PROMPT_BACKEND.md`.
2. **Frontend** Next.js con todas las páginas y el sistema de diseño inicial.
3. **Verificación** con Docker: build, tests, stack levantado.
4. **Rediseño de flujo**: subida en lote, detección del ejecutivo por IA,
   matching difuso, asignación posterior, filtro por fecha (con tests adicionales).
5. **Reestilo** a la identidad corporativa (púrpura Minsait).
6. **Reestilo** al sistema "Aetheric Intelligence" (glassmorphism, paleta Índigo/Slate).
7. **Optimización**: frontend a modo producción (salida standalone) y
   reorganización en este **monorepo** con un único `docker-compose.yml`.
8. **Migración a Groq** como proveedor por defecto (Whisper large v3 + Llama 3.3
   70B, coste $0); el patrón factory mantiene Claude/OpenAI/Azure como opciones.
9. **Rúbrica editable** con subcategorías y categorías que se pueden añadir/eliminar
   (migración `0003`); el prompt de la IA pasa a ser **dinámico**.
10. **Diarización por LLM** (por contenido), dejando la heurística de pausas como
    fallback; filtros del dashboard (campaña/ejecutivo/fechas).
11. **Despliegue gratis en vivo**: Vercel (frontend) + Render (backend + PostgreSQL),
    con **procesamiento inline** (`PROCESS_INLINE=true`) para correr sin Celery/Redis.
12. **Campañas con nota de producto** (migración `0004`): entidad `Campaign`,
    extracción de la oferta desde PDF (pypdf + LLM) y formulario con asistente IA;
    la nota se inyecta en el prompt de análisis.
13. **Rebrand a la identidad oficial Minsait**: paleta Pruno / Gris Cerámica /
    Fucsia, tipografía ForFuture Sans, logo oficial, contenedores achaflanados;
    sustituye a "Aetheric Intelligence" / Índigo/Slate.
14. **Roles admin/jefe/asesor** (migración `0005`) con scoping, login de asesor,
    panel "Mi rendimiento" y **umbrales QA** configurables.
15. **Limpieza de lenguaje a "vista previa para evaluación"** (se elimina el de
    "demo interna"; sin credenciales demo en login ni contraseñas en el seed) y
    **fix de cold-start** (keepalive + resiliencia en el frontend).
