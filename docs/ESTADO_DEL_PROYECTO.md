# 🧠 Estado del Proyecto — CallQA AI

> **Memoria de desarrollo.** Este documento resume lo construido, las decisiones y lo pendiente.
>
> 👉 **Para el estado MÁS ACTUAL y la guía de desarrollo** (cómo correr, testear, desplegar y
> dónde tocar cada cosa), ver **[`AGENTS.md`](AGENTS.md)** y **[`CHANGELOG.md`](CHANGELOG.md)**.

**Última actualización:** Junio 2026
**Estado general:** ✅ MVP funcional **desplegado en producción gratis** (Vercel + Render),
con transcripción y análisis vía **Groq** (coste $0). 33 tests backend en verde.

---

## 1. ¿Qué es CallQA AI?

Plataforma web de **Quality Assurance automatizado** para call centers
bancarios. El supervisor de QA sube grabaciones de llamadas; la IA las
transcribe, identifica al ejecutivo, las evalúa contra una rúbrica de
7 dimensiones y genera un reporte tipo NPS con recomendaciones.

> ⚠️ Es un **prototipo / prueba de concepto interno** para Minsait (Grupo
> Indra). No debe usarse con datos reales de clientes sin aprobación de
> Compliance. Todas las pantallas muestran un banner de aviso.

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

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Procesamiento asíncrono | Celery 5 + Redis |
| Base de datos | PostgreSQL 15 |
| IA — transcripción | Groq API (Whisper large v3) · factory para Whisper local / Azure Speech |
| IA — análisis | Groq (Llama 3.3 70B, gratis) · factory para Claude / OpenAI / Azure |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Datos en frontend | TanStack Query + Axios; estado de sesión con Zustand |
| Gráficos | Recharts |
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
├── backend/                  # API FastAPI + worker Celery
│   ├── app/
│   │   ├── main.py            # Arranque, CORS, logging JSON, routers
│   │   ├── config.py          # Configuración por variables de entorno
│   │   ├── models/            # Tablas SQLAlchemy
│   │   ├── schemas/           # DTOs Pydantic
│   │   ├── routers/           # Endpoints REST
│   │   ├── services/          # Lógica de negocio (IA, storage, matching, PDF)
│   │   ├── tasks/             # Tareas Celery
│   │   └── prompts/           # Prompts para los LLM
│   ├── alembic/               # Migraciones de BD (0001, 0002, 0003)
│   ├── scripts/seed_data.py   # Datos iniciales
│   ├── tests/                 # 33 tests automatizados
│   └── docker-compose.yml     # Compose SOLO del backend (para devs)
│
├── frontend/                 # Aplicación Next.js
│   ├── app/                   # Páginas (login + grupo (main))
│   ├── components/            # UI, layout, charts, dashboard
│   ├── lib/                   # api, auth, queries, utils
│   ├── types/                 # Tipos TypeScript
│   └── Dockerfile             # Imagen de producción (salida standalone)
│
└── docs/                     # TODA la documentación del proyecto
    ├── AGENTS.md              # Guía canónica de desarrollo (la más importante)
    ├── 00_INDICE.md           # Índice de la documentación
    ├── ESTADO_DEL_PROYECTO.md # Este archivo (memoria del proyecto)
    ├── CHANGELOG.md · DEPLOY_GRATIS.md
    ├── 01_…_07_DISEÑO_VISUAL.md  # Especificación de origen (algunos históricos)
    └── DESIGN.md              # Sistema de diseño "Aetheric Intelligence"
```

---

## 4. Funcionalidades implementadas

### Backend

- **Autenticación** JWT (login, refresh, logout, me) con rate limiting en login.
- **Ejecutivos** (agents): alta, edición, baja lógica, estadísticas.
- **Llamadas**: subida individual y **en lote**, listado paginado con filtros
  (ejecutivo, estado, **rango de fechas**, score), detalle, estado para
  polling, reintento, reporte PDF, borrado.
- **Procesamiento asíncrono** (Celery): `QUEUED → TRANSCRIBING → ANALYZING → DONE`.
- **Dashboard / reporte NPS**: KPIs del equipo, distribución de scores,
  rankings, performance por ejecutivo.
- **Configuración**: rúbrica **editable** (7 dimensiones por defecto, con
  subcategorías activables y posibilidad de añadir/eliminar categorías y
  subcategorías; la IA usa las subcategorías activas) e idioma de análisis.
- **Seguridad**: enmascarado de datos sensibles (tarjetas, DNI, CVV) antes de
  enviar texto a la IA; contraseñas con bcrypt; CORS por lista blanca.
- **Patrón factory** para proveedores de IA y transcripción → portable a Azure.

### Frontend

- Login, dashboard, listado/subida/detalle de llamadas, ejecutivos,
  configuración.
- Modo claro / oscuro con toggle persistente.
- Banner de prototipo en todas las pantallas.
- Polling automático del estado de las llamadas en proceso.
- Gráficos: distribución de scores, radar por dimensión, evolución temporal.

---

## 5. Flujo de trabajo (versión actual)

1. El supervisor sube **un grupo de audios MP3**. Solo indica: los archivos,
   la **campaña**, un **comentario opcional** y el **responsable** de la subida.
   No elige ejecutivo.
2. Por cada llamada, la IA transcribe el audio y **detecta el nombre del
   ejecutivo** (siempre se presenta al inicio de la llamada).
3. El nombre detectado se compara (**matching difuso**, tolera erratas como
   "Juan Perz" → "Juan Pérez") con los ejecutivos registrados:
   - **Coincide** → la llamada se asigna a ese ejecutivo.
   - **No coincide** → la llamada queda con el nombre detectado y la etiqueta
     "Sin registrar".
4. El supervisor puede **crear** después al ejecutivo no registrado; al
   crearlo, sus llamadas previas se le **vinculan automáticamente**. También
   puede asignar manualmente desde el detalle de cada llamada.
5. El supervisor consulta el **reporte NPS** (dashboard) y el detalle
   individual de cada llamada/ejecutivo.

---

## 6. Sistema de diseño

Se aplicó el sistema **"Aetheric Intelligence"** (`DESIGN.md`):

- Estética *High-Tech Editorial* + **Glassmorphism**.
- **Modo oscuro** (por defecto): canvas slate-navy `#0b1020` con resplandores
  radiales; **modo claro**: off-white con superficies blancas.
- Acento **Índigo** (`#4f46e5` en claro / `#6366f1` en oscuro) para acciones y
  datos destacados.
- Cards, sidebar, header e inputs como **paneles de cristal** translúcidos con
  desenfoque de fondo; botones con resplandor (glow) en hover.
- Tipografía **Inter**.

> Nota histórica: una iteración previa usó la paleta corporativa púrpura de
> Minsait y, más tarde, una paleta Electric Rose / Deep Plum; ambas fueron
> reemplazadas por la paleta Índigo/Slate actual a petición del cliente.

---

## 7. Modelo de datos (resumen)

| Tabla | Contenido |
|---|---|
| `users` | Supervisores de QA (login) |
| `agents` | Ejecutivos evaluados |
| `calls` | Llamadas subidas; `agent_id` puede ser nulo; `detected_agent_name`, `responsible` |
| `transcriptions` | Transcripción + segmentos con timestamps (1:1 con call) |
| `analyses` | Scores por dimensión, score global, recomendaciones (1:1 con call) |
| `rubric_config` | Rúbrica editable: 7 dimensiones por defecto con sus pesos, subcategorías activables y categorías/subcategorías que se pueden añadir o eliminar |
| `app_settings` | Configuración global (idioma, proveedor IA) |

Migraciones: **0001** esquema inicial · **0002** detección de ejecutivo
(`agent_id` nullable + `detected_agent_name` + `responsible`) · **0003**
rúbrica editable (`rubric_config.criteria` JSON con subcategorías).

---

## 8. Cómo ejecutarlo

Requisito: **Docker Desktop** abierto.

```bash
cd callqa-ai
docker compose up --build
```

- Frontend: <http://localhost:3000>
- API / docs: <http://localhost:8000/docs>
- Credenciales demo: `admin@callqa.com` / `Admin123!`

Para detener: `Ctrl+C` o `docker compose down`.

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

## 9. Verificaciones realizadas

| Verificación | Resultado |
|---|---|
| Build Docker del backend | ✅ |
| Tests del backend (`pytest`) | ✅ 33/33 |
| Migraciones 0001 + 0002 + 0003 | ✅ aplican sin error |
| Build de producción del frontend | ✅ 10 rutas, tipos TS válidos |
| Endpoints API (login, agents, calls, dashboard, config) | ✅ |
| CORS frontend ↔ backend | ✅ |
| Subida en lote, filtro por fecha, asignación, auto-vínculo | ✅ |
| Matching difuso de nombres | ✅ (test unitario) |

---

## 10. Pendientes / próximos pasos

- [x] **Despliegue en la nube** (frontend → Vercel, backend + PostgreSQL → Render),
      **gratis** y en vivo. Ver `DEPLOY_GRATIS.md`.
- [x] **Groq configurado** (`GROQ_API_KEY` real) haciendo transcripción y análisis
      en producción. Pendiente: validación end-to-end exhaustiva con audios reales.
- [ ] Reproductor de audio sincronizado con la transcripción (la API aún no
      expone un endpoint para servir el audio).
- [ ] Endpoint de exportación masiva (CSV) del reporte del equipo.
- [ ] Antes de producción: validaciones de Compliance, DPO y Seguridad
      (ver `01_VISION_Y_CASOS_DE_USO.md`, sección 7).

---

## 11. Historial de iteraciones

1. **Generación inicial** del backend completo (FastAPI + Celery + modelo de
   datos + tests) a partir del prompt maestro de `04_PROMPT_BACKEND.md`.
2. **Frontend** Next.js con todas las páginas y el sistema de diseño inicial.
3. **Verificación** con Docker: build, tests, stack levantado.
4. **Rediseño de flujo**: subida en lote, detección del ejecutivo por IA,
   matching difuso, asignación posterior, filtro por fecha (con tests
   adicionales hasta llegar a los 33 actuales).
5. **Reestilo** a la identidad corporativa (púrpura Minsait).
6. **Reestilo** al sistema "Aetheric Intelligence" (glassmorphism).
7. **Optimización**: frontend a modo producción (salida standalone) y
   reorganización en este **monorepo** con un único `docker-compose.yml`.
8. **Migración a Groq** como proveedor por defecto (Whisper large v3 + Llama 3.3
   70B, coste $0); el patrón factory mantiene Claude/OpenAI/Azure como opciones.
9. **Rúbrica editable** con subcategorías y categorías que se pueden añadir/eliminar
   (migración `0003`); el prompt de la IA pasa a ser **dinámico**.
10. **Diarización por LLM** (por contenido), dejando la heurística de pausas como
    fallback; filtros del dashboard (campaña/ejecutivo/fechas) y **paleta Índigo/Slate**.
11. **Despliegue gratis en vivo**: Vercel (frontend) + Render (backend + PostgreSQL),
    con **procesamiento inline** (`PROCESS_INLINE=true`) para correr sin Celery/Redis.
