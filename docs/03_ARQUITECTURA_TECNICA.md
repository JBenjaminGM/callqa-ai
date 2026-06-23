# 🏗️ Arquitectura Técnica

**Proyecto:** CallQA AI — prototipo (vista previa para evaluación)
**Estado:** desplegado en vivo (Vercel + Render, coste $0) · proveedor de IA por defecto: Groq

---

## 1. Stack Tecnológico

### Backend
| Componente | Tecnología | Razón |
|---|---|---|
| Lenguaje | Python 3.11+ | Mejor ecosistema para IA/audio |
| Framework web | FastAPI | Rápido, tipado, OpenAPI automático |
| ORM | SQLAlchemy 2.0 + Alembic | Estándar de la industria, migraciones |
| Validación | Pydantic v2 | Integrado con FastAPI |
| Cola de tareas | Celery 5 + Redis (modo local) | Procesamiento asíncrono de audios |
| Base de datos | PostgreSQL 15 | Confiable, escalable, JSON nativo |
| Storage de audios | Disco local / Amazon S3 (boto3) | Persistencia de archivos |
| Lectura de PDF | pypdf | Parseo de notas de producto de campañas |
| Generación de PDF | reportlab | Reporte de evaluación por llamada |
| Rate limiting | slowapi | Protección del endpoint de login |
| Auth | JWT (python-jose) + bcrypt (passlib) | Estándar, sin dependencias externas |
| HTTP a IA | httpx | Cliente de Groq/Claude/OpenAI/Azure |

### Frontend
| Componente | Tecnología | Razón |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR/SSG, TypeScript, Vercel-friendly |
| UI / estilos | Tailwind CSS (identidad Minsait) | Moderno, accesible, customizable |
| Tipografía | ForFuture Sans (woff2 locales) | Tipografía oficial de marca Minsait |
| Charts | Recharts | Ligero, integra bien con React |
| HTTP client | Axios + TanStack Query | Caching y revalidación automática |
| State | Zustand | Simple, sin boilerplate de Redux |

### Servicios externos
| Servicio | Uso | Costo aprox |
|---|---|---|
| **Groq API** | Transcripción (Whisper large v3) **y análisis por defecto** (Llama 3.3 70B) | Gratis hasta cuota (luego ~$0.04/hora audio en transcripción) |
| **Anthropic Claude API** (alternativa) | Análisis de transcripción (configurable) | ~$0.01-0.03 por llamada |
| **OpenAI API** (alternativa) | Análisis (configurable) | ~$0.01-0.03 por llamada |
| **Resend** (opcional) | Envío de emails | Gratis hasta 100/día |

### Infraestructura (despliegue en vivo)
| Componente | Plataforma | Costo |
|---|---|---|
| Backend hosting | Render (tier gratuito) | $0 |
| Frontend hosting | Vercel (Hobby tier) | $0 |
| Base de datos | Render PostgreSQL (tier gratuito) | $0 |
| Storage de audios | Disco local del backend (o AWS S3) | $0 |

**Costo total del despliegue actual:** **$0** (Groq gratis + tiers gratuitos de
Vercel/Render). El tier gratuito de Render **no ofrece workers**, por lo que el
backend procesa los audios **inline** (`PROCESS_INLINE=true`, vía
`BackgroundTasks` de FastAPI), sin Celery ni Redis. La cola Celery 5 + Redis
sólo se usa en el entorno local con `docker-compose` (ver sección 2).

> **Arranque en frío (cold-start):** el plan gratuito de Render duerme el backend
> tras ~15 min de inactividad; el primer arranque en frío tarda ~50 s y puede
> percibirse como un "error de API". Se mitiga con un **GitHub Action**
> (`.github/workflows/keepalive.yml`) que hace ping a `/health` cada 12 min, más
> resiliencia en el frontend (`frontend/lib/api.ts`: timeout de 90 s, reintentos
> en cold-start y el mensaje "activando el servidor"). El PostgreSQL gratuito de
> Render **caduca a los 90 días**.

---

## 2. Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│              USUARIO (admin / jefe / asesor)                     │
│                       Browser (Chrome/Edge)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND (Vercel)                          │
│                    Next.js 14 + Tailwind                         │
│                 https://callqa-ai.vercel.app                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (Render)                          │
│                    FastAPI + Python 3.11                         │
│                https://callqa-api.onrender.com                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Auth │ Llamadas │ Ejecutivos │ Campañas │ Dashboard │Conf│    │
│  └─────────────────────────────────────────────────────────┘    │
└──────┬─────────────────┬──────────────────┬────────────────────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌──────────────┐  ┌────────────┐  ┌──────────────────────────┐
│ PostgreSQL   │  │   Redis    │  │  Procesamiento           │
│ (Render)     │  │  (sólo     │  │  - Transcripción         │
│              │  │  local)    │  │  - Análisis IA           │
└──────────────┘  └─────┬──────┘  └────┬─────────────────┬───┘
                        │              │                 │
                        └──────────────┘                 │
                                                         │
                                       ┌─────────────────┼──────────────┐
                                       ▼                 ▼              ▼
                                 ┌──────────┐    ┌─────────────┐  ┌──────────┐
                                 │   Groq   │    │  Anthropic  │  │  OpenAI  │
                                 │  API     │    │  Claude API │  │  API     │
                                 │ (Whisper)│    │             │  │          │
                                 └──────────┘    └─────────────┘  └──────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  STORAGE DE AUDIOS                               │
│             Disco local del backend o AWS S3                     │
└─────────────────────────────────────────────────────────────────┘
```

> **Nota (proveedor de IA):** por defecto el análisis lo realiza **Groq (Llama
> 3.3 70B)**, el mismo proveedor usado para la transcripción (Whisper large v3).
> Anthropic Claude y OpenAI aparecen en el diagrama como **alternativas
> configurables** (patrón factory) del servicio de análisis.
>
> **Nota (dos modos de procesamiento):** el diagrama muestra el camino con
> **Celery + Redis**, que es el que se usa en el **entorno local con
> `docker-compose`**. En el **despliegue en vivo en Render** (tier gratuito, sin
> workers) el backend procesa el audio **inline** dentro del propio proceso de
> la API mediante `BackgroundTasks` (`PROCESS_INLINE=true`); en ese modo no hay
> Redis ni worker Celery. La lógica de transcripción y análisis es la misma en
> ambos casos.

---

## 3. Flujo de Procesamiento de una Llamada

```
1. Un manager (admin/jefe) sube audio vía frontend
   └─► POST /api/v1/calls (multipart/form-data)
        │
        ├─► Backend guarda archivo en storage
        ├─► Crea registro en BD con status="QUEUED"
        ├─► Lanza el procesamiento (worker Celery en local /
        │     tarea inline con BackgroundTasks si PROCESS_INLINE=true)
        └─► Responde 202 Accepted con call_id

2. El procesador toma la tarea
        │
        ├─► Marca status="TRANSCRIBING"
        ├─► Descarga audio del storage
        ├─► Envía a Groq API (Whisper large v3)
        ├─► Guarda transcripción en BD
        └─► Marca status="ANALYZING"

3. El procesador continúa con el análisis
        │
        ├─► Enmascara datos sensibles (best-effort, regex)
        ├─► Construye prompt con la rúbrica dinámica + transcripción
        │     (+ nota de producto de la campaña, si la llamada tiene
        │      campaign_id, para evaluar la oferta ofrecida)
        ├─► Envía al LLM configurado (Groq Llama 3.3 70B por defecto)
        ├─► Parsea respuesta JSON (scores + recomendaciones)
        ├─► Guarda análisis en BD
        └─► Marca status="DONE"

4. Frontend hace polling cada 5 segundos
        │
        └─► GET /api/v1/calls/{id}/status
             Cuando status="DONE", redirige al detalle
```

---

## 4. Modelo de Datos

### Diagrama entidad-relación

```
┌──────────────────┐         ┌──────────────────┐
│      users       │         │     agents       │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │  agent_ │ id (PK)          │
│ email (unique)   │◄───id───│ name             │
│ password_hash    │  (FK,   │ email            │
│ name             │  null)  │ campaign         │
│ role             │         │ start_date       │
│ agent_id (FK)    │         │ active           │
│ created_at       │         │ created_at       │
│ last_login       │         └────────┬─────────┘
└──────────────────┘                  │
                                      │ 1:N
   ┌──────────────────────┐           ▼
   │     campaigns        │  ┌──────────────────────┐
   ├──────────────────────┤  │       calls          │
   │ id (PK)              │  ├──────────────────────┤
   │ name                 │  │ id (PK)              │
   │ product_service      │  │ agent_id (FK, null)  │
   │ offer_description    │◄─│ campaign_id (FK)     │
   │ key_benefits         │c │ uploaded_by (FK)     │
   │ price_conditions     │a │ campaign_type        │
   │ client_requirements  │m │ detected_agent_name  │
   │ mandatory_phrases    │p │ responsible          │
   │ forbidden_claims     │a │ audio_url            │
   │ target_audience      │i │ duration_seconds     │
   │ notes                │g │ language             │
   │ source               │n │ status (enum)        │
   │ active               │_ │ call_date            │
   │ created_at           │id│ call_reason          │
   └──────────────────────┘  │ error_message        │
                             │ created_at           │
                             │ processed_at         │
                             └──────────┬───────────┘
                                        │
                          ┌─────────────┴──────────────┐
                          │ 1:1                        │ 1:1
                          ▼                            ▼
                ┌──────────────────┐          ┌──────────────────────┐
                │ transcriptions   │          │     analyses         │
                ├──────────────────┤          ├──────────────────────┤
                │ id (PK)          │          │ id (PK)              │
                │ call_id (FK)     │          │ call_id (FK)         │
                │ full_text        │          │ global_score         │
                │ segments (JSONB) │          │ dimension_scores(JB) │
                │ language         │          │ recommendations(JB)  │
                │ created_at       │          │ summary              │
                └──────────────────┘          │ ai_provider          │
                                              │ created_at           │
                                              └──────────────────────┘

┌──────────────────────┐
│  rubric_config       │
├──────────────────────┤
│ id (PK)              │
│ dimension_key        │
│ dimension_name       │
│ description          │
│ weight (decimal)     │
│ criteria (JSONB)     │  ← subcriterios activables
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│   app_settings       │  ← idioma, proveedor IA y umbrales QA (qa_*)
├──────────────────────┤
│ key (PK)             │
│ value                │
│ updated_at           │
└──────────────────────┘
```

> **Roles:** `users.role` ∈ {`admin`, `jefe`, `asesor`} (default `jefe`).
> `admin` y `jefe` comparten permisos (gestión + analítica global; helper
> `is_manager`). `users.agent_id` enlaza una cuenta **asesor** con su ficha de
> ejecutivo (`agents`); es `NULL` para admin/jefe. Las llamadas guardan el
> nuevo `campaign_id` (FK a `campaigns`) y conservan `campaign_type` (texto)
> por compatibilidad y para los filtros del dashboard.

### Definición de tablas (SQL)

```sql
-- Usuarios del sistema (admin / jefe / asesor)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'jefe',  -- 'admin' | 'jefe' | 'asesor'
    agent_id INT REFERENCES agents(id),  -- enlaza un asesor con su ficha; NULL para admin/jefe
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Ejecutivos evaluados (un asesor puede tener cuenta de usuario)
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    campaign VARCHAR(100),
    start_date DATE,
    active BOOLEAN DEFAULT TRUE,
    photo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Campañas con nota de producto (9 campos de oferta)
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    product_service TEXT,       -- producto / servicio
    offer_description TEXT,      -- descripción de la oferta
    key_benefits TEXT,          -- beneficios clave
    price_conditions TEXT,      -- precio / condiciones
    client_requirements TEXT,   -- requisitos del cliente
    mandatory_phrases TEXT,     -- frases obligatorias
    forbidden_claims TEXT,      -- claims prohibidos
    target_audience TEXT,       -- público objetivo
    notes TEXT,                 -- notas
    source VARCHAR(50),         -- 'form' | 'pdf' | 'ai'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Llamadas subidas para análisis
CREATE TYPE call_status AS ENUM ('QUEUED', 'TRANSCRIBING', 'ANALYZING', 'DONE', 'ERROR');

CREATE TABLE calls (
    id SERIAL PRIMARY KEY,
    agent_id INT REFERENCES agents(id),  -- nullable: el ejecutivo se detecta tras transcribir
    campaign_id INT REFERENCES campaigns(id),  -- nota de producto a evaluar
    uploaded_by INT NOT NULL REFERENCES users(id),
    detected_agent_name VARCHAR(255),  -- nombre detectado por el LLM
    responsible VARCHAR(255),          -- ejecutivo responsable confirmado
    audio_url VARCHAR(500) NOT NULL,
    audio_filename VARCHAR(255),
    duration_seconds INT,
    file_size_bytes BIGINT,
    language VARCHAR(10) DEFAULT 'es',
    status call_status DEFAULT 'QUEUED',
    call_date DATE,
    campaign_type VARCHAR(100),  -- texto, se conserva por compatibilidad y filtros
    call_reason TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

CREATE INDEX idx_calls_agent ON calls(agent_id);
CREATE INDEX idx_calls_campaign ON calls(campaign_id);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_created ON calls(created_at DESC);

-- Transcripciones (relación 1:1 con calls)
CREATE TABLE transcriptions (
    id SERIAL PRIMARY KEY,
    call_id INT UNIQUE NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    full_text TEXT NOT NULL,
    segments JSONB,  -- [{start, end, speaker, text}]
    language VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Análisis IA (relación 1:1 con calls)
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    call_id INT UNIQUE NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    global_score INT CHECK (global_score >= 0 AND global_score <= 100),
    dimension_scores JSONB NOT NULL,  -- {greeting: 85, assertiveness: 72, ...}
    recommendations JSONB,  -- [{priority, title, description}]
    summary TEXT,
    ai_provider VARCHAR(50),  -- 'groq', 'claude', 'openai' o 'azure'
    ai_model VARCHAR(100),
    tokens_used INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Configuración de la rúbrica (rúbrica dinámica con subcriterios)
CREATE TABLE rubric_config (
    id SERIAL PRIMARY KEY,
    dimension_key VARCHAR(50) UNIQUE NOT NULL,
    dimension_name VARCHAR(255) NOT NULL,
    description TEXT,
    weight DECIMAL(5,2) NOT NULL,  -- Suma de pesos = 100.00
    criteria JSONB,  -- subcriterios activables por dimensión
    display_order INT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Settings globales (clave-valor: idioma, proveedor IA y umbrales QA)
CREATE TABLE app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Datos iniciales de la rúbrica
INSERT INTO rubric_config (dimension_key, dimension_name, weight, display_order) VALUES
('greeting', 'Saludo y protocolo de apertura/cierre', 14.28, 1),
('assertiveness', 'Asertividad y tono', 14.28, 2),
('promotions', 'Mención correcta de promociones/productos', 14.28, 3),
('compliance', 'Cumplimiento normativo', 14.28, 4),
('resolution', 'Resolución efectiva del motivo', 14.28, 5),
('objections', 'Manejo de objeciones', 14.28, 6),
('sentiment', 'Detección de sentimiento del cliente', 14.32, 7);

INSERT INTO app_settings (key, value) VALUES
('default_language', 'es'),
('ai_provider', 'groq'),
('whisper_provider', 'groq'),
-- Umbrales QA configurables (sólo editables por un manager)
('qa_target_score', '90'),         -- score objetivo
('qa_low_agent_threshold', '80'),  -- umbral de asesor con bajo rendimiento
('qa_red_call_threshold', '60'),   -- umbral de llamada crítica (roja)
('qa_min_calls_ranking', '5'),     -- mínimo de llamadas para entrar al ranking
('qa_trend_drop_alert', '5');      -- caída de tendencia que dispara alerta
```

---

## 5. API Contracts (Endpoints REST)

### Convenciones generales

- Base URL: `https://callqa-api.onrender.com/api/v1`
- Autenticación: `Authorization: Bearer <JWT>` en todos los endpoints salvo `POST /auth/login`
- Formato: JSON
- Códigos de respuesta estándar HTTP

#### Permisos por rol

Hay **3 roles**: `admin` y `jefe` comparten permisos (gestión + analítica
global, vía la dependencia `require_manager`); `asesor` sólo ve **su propio**
rendimiento. Notación en este documento:

- **[manager]** — sólo admin/jefe; un asesor recibe **403**.
- **[scoped]** — accesible por asesor pero **limitado a sus propios datos**
  (su ficha, sus llamadas, su panel "Mi rendimiento").

Resumen de la superficie de la API (todo bajo `/api/v1`):

| Recurso | Endpoint | Permiso |
|---|---|---|
| Auth | `POST /auth/login` (rate limit 5/15min), `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me` | público (login) / autenticado |
| Ejecutivos | `GET /agents` | [scoped] (asesor sólo su ficha) |
| | `POST /agents`, `POST /agents/{id}/login`, `PUT /agents/{id}`, `DELETE /agents/{id}` | [manager] |
| | `GET /agents/{id}` | [scoped] |
| Campañas | `GET /campaigns`, `POST /campaigns`, `GET /campaigns/{id}`, `PUT /campaigns/{id}`, `DELETE /campaigns/{id}`, `POST /campaigns/extract` (PDF), `POST /campaigns/assist` (IA) | [manager] |
| Llamadas | `POST /calls`, `POST /calls/batch`, `PUT /calls/{id}/assign`, `POST /calls/{id}/retry`, `DELETE /calls/{id}` | [manager] |
| | `GET /calls`, `GET /calls/{id}`, `GET /calls/{id}/status`, `GET /calls/{id}/report.pdf` | [scoped] |
| Dashboard | `GET /dashboard/summary`, `GET /dashboard/campaigns` | [manager] |
| | `GET /dashboard/agents/{id}` | [scoped] |
| Configuración | `GET /config/rubric`, `GET /config/settings` | autenticado |
| | `PUT /config/rubric`, `PUT /config/settings` (incluye umbrales QA) | [manager] |

### Autenticación

#### POST `/auth/login` (público · rate limit 5/15min)
**Body:**
```json
{ "email": "jefe@callqa.com", "password": "..." }
```
**Respuesta 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": { "id": 1, "name": "Juan Pérez", "email": "...", "role": "jefe", "agent_id": null }
}
```

#### POST `/auth/refresh`
**Respuesta 200:** Nuevo access token

#### POST `/auth/logout`
**Respuesta 204**

#### GET `/auth/me`
**Respuesta 200:** Usuario autenticado, incluyendo `role` y `agent_id` (el
frontend los usa para la navegación y la redirección por rol: asesor →
`/mi-panel`, admin/jefe → `/dashboard`).

---

### Ejecutivos

#### GET `/agents` [scoped]
Un asesor sólo recibe **su propia** ficha.
**Query params:** `?active=true&search=juan`
**Respuesta 200:**
```json
[
  {
    "id": 1,
    "name": "María González",
    "email": "maria@banco.com",
    "campaign": "Tarjetas Premium",
    "start_date": "2024-01-15",
    "active": true
  }
]
```

#### POST `/agents` [manager]
**Body:**
```json
{
  "name": "Carlos Ruiz",
  "email": "carlos@banco.com",
  "campaign": "Préstamos",
  "start_date": "2024-03-01"
}
```
**Respuesta 201:** Objeto agente creado

#### POST `/agents/{id}/login` [manager]
Crea la cuenta de usuario **asesor** para ese ejecutivo y enlaza
`User.agent_id` ↔ `agents.id`. El asesor entra con el email del ejecutivo.
**Respuesta 201:** Credenciales / usuario creado

#### GET `/agents/{id}` [scoped]
**Respuesta 200:** Detalle del agente + estadísticas (score promedio, total de llamadas)

#### PUT `/agents/{id}` [manager]
**Body:** Campos a actualizar
**Respuesta 200:** Objeto actualizado

#### DELETE `/agents/{id}` [manager] (soft delete)
**Respuesta 204**

---

### Campañas

Cada campaña tiene una **nota de producto** de 9 campos. La nota se inyecta en
el prompt de análisis para evaluar si el ejecutivo ofreció la oferta correcta
(integrado en los criterios `promotions`/`compliance` de la rúbrica). Todos los
endpoints son **[manager]**.

#### GET `/campaigns` · POST `/campaigns` · GET `/campaigns/{id}` · PUT `/campaigns/{id}` · DELETE `/campaigns/{id}`
CRUD estándar de campañas (los 9 campos de la nota + `name`, `source`, `active`).

#### POST `/campaigns/extract`
**Body (multipart/form-data):** un PDF. La IA lo parsea (pypdf + LLM) y
autocompleta los campos de la nota que encuentre; lo que falte se completa en el
formulario.
**Respuesta 200:** Nota de producto parcial/completa propuesta

#### POST `/campaigns/assist`
Asistente IA que ayuda a redactar/completar la nota de producto desde el
formulario.
**Respuesta 200:** Sugerencias para los campos de la nota

---

### Llamadas

#### POST `/calls` [manager]
**Body (multipart/form-data):**
- `audio`: archivo de audio
- `agent_id`: int (opcional; el ejecutivo se puede detectar tras transcribir)
- `campaign_id`: int (opcional; campaña cuya nota de producto se evaluará)
- `call_date`: ISO date (opcional)
- `campaign_type`: string (opcional)
- `call_reason`: string (opcional)

**Respuesta 202:**
```json
{
  "id": 123,
  "status": "QUEUED",
  "agent_id": 1,
  "estimated_completion_seconds": 180
}
```

#### POST `/calls/batch` [manager]
**Body (multipart/form-data):** múltiples archivos
**Respuesta 202:** lista de IDs creados

#### GET `/calls` [scoped]
Un asesor sólo ve **sus propias** llamadas.
**Query params:**
- `agent_id`: int (opcional)
- `campaign_id`: int (opcional)
- `status`: enum (opcional)
- `date_from`, `date_to`: ISO date
- `min_score`, `max_score`: int
- `page`: int (default 1)
- `page_size`: int (default 50)
- `sort_by`: string (default 'created_at')
- `sort_order`: 'asc' | 'desc'

**Respuesta 200:**
```json
{
  "items": [
    {
      "id": 123,
      "agent": { "id": 1, "name": "María González" },
      "call_date": "2026-05-18",
      "duration_seconds": 487,
      "status": "DONE",
      "global_score": 78,
      "created_at": "2026-05-19T10:30:00Z"
    }
  ],
  "total": 245,
  "page": 1,
  "page_size": 50,
  "total_pages": 5
}
```

#### GET `/calls/{id}` [scoped]
**Respuesta 200:**
```json
{
  "id": 123,
  "agent": { "id": 1, "name": "María González", "campaign": "..." },
  "audio_url": "https://...",
  "duration_seconds": 487,
  "status": "DONE",
  "call_date": "2026-05-18",
  "campaign_type": "Tarjetas Premium",
  "transcription": {
    "full_text": "...",
    "segments": [
      { "start": 0.0, "end": 5.2, "speaker": "agent", "text": "Buenos días..." },
      { "start": 5.2, "end": 9.8, "speaker": "customer", "text": "Hola..." }
    ]
  },
  "analysis": {
    "global_score": 78,
    "dimension_scores": {
      "greeting": 90,
      "assertiveness": 75,
      "promotions": 60,
      "compliance": 85,
      "resolution": 80,
      "objections": 70,
      "sentiment": 85
    },
    "recommendations": [
      {
        "priority": "high",
        "dimension": "promotions",
        "title": "Mencionar promoción vigente",
        "description": "El ejecutivo no mencionó la promo X que era relevante para este cliente."
      }
    ],
    "summary": "Llamada con buen tono general...",
    "team_average": {
      "greeting": 82,
      "assertiveness": 78,
      "...": "..."
    }
  }
}
```

#### GET `/calls/{id}/status` [scoped]
**Respuesta 200:** Solo el status (para polling rápido)
```json
{ "id": 123, "status": "ANALYZING", "progress_percent": 65 }
```

#### PUT `/calls/{id}/assign` [manager]
Asigna/reasigna el ejecutivo responsable de la llamada (tras la detección
automática).
**Respuesta 200:** Llamada actualizada

#### POST `/calls/{id}/retry` [manager]
Reintenta el procesamiento (idempotente).
**Respuesta 202**

#### GET `/calls/{id}/report.pdf` [scoped]
**Respuesta 200:** Archivo PDF binario (el PDF lleva el sello "Vista previa para
evaluación").

#### DELETE `/calls/{id}` [manager]
**Respuesta 204**

---

### Dashboard

#### GET `/dashboard/summary` [manager]
**Query params:** `?period=30d` (7d, 30d, 90d) · también filtra por
`campaign`/`campaign_id`, `agent_id` y rango de fechas.
**Respuesta 200:**
```json
{
  "total_calls": 245,
  "average_score": 76.5,
  "score_trend": "+2.3",
  "calls_by_day": [
    { "date": "2026-05-13", "count": 12, "avg_score": 75 }
  ],
  "score_distribution": [
    { "range": "0-59", "count": 32 },
    { "range": "60-79", "count": 145 },
    { "range": "80-100", "count": 68 }
  ],
  "top_performers": [
    { "agent_id": 1, "name": "...", "avg_score": 89 }
  ],
  "improvement_opportunities": [
    { "agent_id": 5, "name": "...", "avg_score": 58 }
  ]
}
```

#### GET `/dashboard/campaigns` [manager]
**Query params:** `?period=30d`
**Respuesta 200:** Resumen agregado por campaña (volumen y score medio por
campaña).

#### GET `/dashboard/agents/{id}` [scoped]
**Query params:** `?period=30d`
**Respuesta 200:**
```json
{
  "agent": { "id": 1, "name": "..." },
  "total_calls": 32,
  "average_score": 81,
  "score_trend": "+5.2",
  "dimension_averages": { "greeting": 85, "...": "..." },
  "team_dimension_averages": { "greeting": 78, "...": "..." },
  "strengths": ["greeting", "compliance"],
  "improvement_areas": ["promotions", "objections"],
  "timeline": [
    { "date": "2026-05-01", "avg_score": 76 }
  ]
}
```

---

### Configuración

#### GET `/config/rubric`
**Respuesta 200:** Array de dimensiones con pesos y sus subcriterios activables.

#### PUT `/config/rubric` [manager]
**Body:** Array con `dimension_key`, `weight` (suma = 100) y `criteria`.
**Respuesta 200**

#### GET `/config/settings`
**Respuesta 200:**
```json
{
  "default_language": "es",
  "ai_provider": "groq",
  "qa_target_score": 90,
  "qa_low_agent_threshold": 80,
  "qa_red_call_threshold": 60,
  "qa_min_calls_ranking": 5,
  "qa_trend_drop_alert": 5
}
```

#### PUT `/config/settings` [manager]
**Body:** Objeto con configs a actualizar (incluye los umbrales QA `qa_*`).
**Respuesta 200**

---

## 6. Estructura de Carpetas

### Backend (`/backend`)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings (Pydantic Settings)
│   ├── database.py             # SQLAlchemy engine + session
│   ├── dependencies.py         # FastAPI dependencies (auth, db, require_manager)
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py             # role + agent_id
│   │   ├── agent.py
│   │   ├── campaign.py         # nota de producto (9 campos)
│   │   ├── call.py             # campaign_id + detected_agent_name + responsible
│   │   ├── transcription.py
│   │   ├── analysis.py
│   │   └── config.py
│   │
│   ├── schemas/                # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── agent.py
│   │   ├── campaign.py
│   │   ├── call.py
│   │   ├── analysis.py
│   │   └── dashboard.py
│   │
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── agents.py           # incluye POST /{id}/login
│   │   ├── campaigns.py        # CRUD + /extract (PDF) + /assist (IA)
│   │   ├── calls.py
│   │   ├── dashboard.py
│   │   └── config.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── agent_service.py
│   │   ├── campaign_service.py # parseo de PDF (pypdf) + asistente IA
│   │   ├── call_service.py
│   │   ├── storage_service.py  # Disco local / S3
│   │   ├── transcription_service.py  # Groq Whisper / Whisper local
│   │   ├── analysis_service.py       # Groq (def.) / Claude / OpenAI / Azure
│   │   ├── pdf_service.py             # genera el reporte (reportlab)
│   │   └── masking_service.py        # Enmascarar datos sensibles
│   │
│   ├── tasks/                  # Celery tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── call_tasks.py       # process_call task
│   │
│   ├── prompts/                # Prompts para LLMs
│   │   ├── analysis_es.py
│   │   └── analysis_en.py
│   │
│   └── utils/
│       ├── security.py         # JWT, hashing
│       └── audio.py            # Validación de archivos
│
├── alembic/                    # Migraciones DB (0001–0005)
├── tests/                      # 61 tests (pytest, SQLite en memoria, externos mockeados)
│   ├── conftest.py
│   ├── test_auth.py            # auth + roles/scoping (admin/jefe/asesor)
│   ├── test_agents.py          # incluye creación de login de asesor
│   ├── test_campaigns.py
│   ├── test_calls.py           # idempotencia del retry, modo inline
│   └── test_analysis.py        # score, enmascarado, matching difuso, umbrales QA
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml          # Para desarrollo local
├── requirements.txt
├── alembic.ini
└── README.md
```

### Frontend (`/frontend`)

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── globals.css             # tokens de color Minsait (fuente de verdad)
│   ├── page.tsx                # Landing / redirect por rol
│   ├── login/page.tsx          # (no muestra credenciales demo)
│   ├── dashboard/page.tsx      # admin/jefe
│   ├── mi-panel/page.tsx       # asesor: "Mi rendimiento"
│   ├── calls/
│   │   ├── page.tsx            # Listado
│   │   ├── new/page.tsx        # Subida
│   │   └── [id]/page.tsx       # Detalle
│   ├── agents/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   ├── campaigns/             # lista, crear (PDF/IA/formulario), editar
│   │   ├── page.tsx
│   │   ├── new/page.tsx
│   │   └── [id]/page.tsx
│   └── settings/
│       └── page.tsx
│
├── components/
│   ├── ui/                     # componentes base (estilo Minsait)
│   ├── layout/                 # Sidebar (Pruno + logo blanco), Header
│   ├── calls/                  # CallTable, CallDetail, UploadForm
│   ├── campaigns/              # CampaignForm, PDF/IA import
│   ├── dashboard/              # KPICards, Charts
│   └── shared/                 # Loaders, ErrorBoundary, guard por rol
│
├── lib/
│   ├── api.ts                  # Axios + resiliencia de cold-start (timeout 90s, reintentos)
│   ├── auth.ts                 # Auth helpers + navegación/redirección por rol
│   ├── queries.ts              # TanStack Query hooks
│   └── utils.ts
│
├── types/                      # TypeScript types
├── public/
│   ├── brand/                  # logo oficial Minsait
│   └── fonts/                  # ForFuture Sans (woff2)
├── .env.local.example
├── next.config.js
├── tailwind.config.ts          # paleta Minsait (fuente de verdad)
├── package.json
└── README.md
```

---

## 7. Variables de Entorno

### Backend `.env.example`

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/callqa
REDIS_URL=redis://localhost:6379/0

# Storage
STORAGE_PROVIDER=local  # local | s3
STORAGE_PATH=/data/audios  # si local
AWS_S3_BUCKET=          # si s3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Transcription
WHISPER_PROVIDER=groq   # groq | local
GROQ_API_KEY=

# AI Analysis
AI_PROVIDER=groq        # groq | claude | openai | azure
AI_MODEL_GROQ=llama-3.3-70b-versatile
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
AI_MODEL_CLAUDE=claude-sonnet-4-6
AI_MODEL_OPENAI=gpt-4o

# Azure OpenAI (para migración futura a infraestructura Indra)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Speech (alternativa futura a Groq)
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=eastus

# Auth
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8

# App
APP_ENV=production
APP_DEFAULT_LANGUAGE=es
APP_MAX_AUDIO_SIZE_MB=100
CORS_ORIGINS=https://callqa-ai.vercel.app,http://localhost:3000

# Procesamiento
# false = usa worker Celery (local/docker-compose);
# true  = procesa inline en la propia API, sin worker (Render free)
PROCESS_INLINE=false
```

### Frontend `.env.local.example`

```bash
NEXT_PUBLIC_API_URL=https://callqa-api.onrender.com/api/v1
```

---

## 8. Consideraciones de Seguridad

| Aspecto | Implementación |
|---|---|
| Contraseñas | bcrypt con cost factor 12 |
| Tokens | JWT firmados con HS256, secret rotable |
| CORS | Lista blanca de orígenes |
| Datos sensibles | Regex para enmascarar tarjetas, DNI, CVV |
| API Keys | Solo en variables de entorno, nunca en código |
| Inputs | Validación con Pydantic en backend, Zod en frontend |
| Rate limiting | slowapi en endpoints de login (5 intentos/15min) |
| HTTPS | Forzado en producción (Render/Vercel lo manejan) |
| SQL Injection | Mitigado por SQLAlchemy ORM |
| XSS | Mitigado por React (escape automático) |

---

## 9. Plan de Migraciones

Las migraciones de la BD se manejan con **Alembic**. Comandos clave:

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Historial de migraciones (hasta `0005`)

| Rev | Descripción |
|---|---|
| **0001** | Esquema inicial (users, agents, calls, transcriptions, analyses, rubric_config, app_settings). |
| **0002** | Detección de ejecutivo: `calls.agent_id` pasa a nullable + `detected_agent_name` + `responsible`. |
| **0003** | Rúbrica con subcriterios: añade `rubric_config.criteria` (JSON). |
| **0004** | Campañas: nueva tabla `campaigns` + `calls.campaign_id` (FK) + backfill de las campañas existentes. |
| **0005** | Roles de usuario: añade `users.agent_id` (FK) + backfill de rol `'supervisor'` → `'jefe'`. |

En el despliegue en vivo (Render) las migraciones se ejecutan automáticamente al
arrancar: el comando de arranque (`alembic upgrade head` + seed + `uvicorn`) vive
en el **CMD del `Dockerfile`**. El archivo `backend/railway.json` se conserva como
referencia para un despliegue alternativo en Railway, pero no es el entorno actual.

> **Seed:** crea las cuentas sembradas `admin@callqa.com` (admin),
> `jefe@callqa.com` (jefe) y un **asesor por cada ejecutivo demo** (email del
> ejecutivo, contraseña `Asesor123!`), 3 campañas de ejemplo con su nota de
> producto, y los umbrales QA por defecto. El seed **ya no imprime contraseñas** y
> el login **ya no muestra credenciales demo**.
