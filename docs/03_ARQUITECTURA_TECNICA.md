# 🏗️ Arquitectura Técnica

**Proyecto:** CallQA AI
**Versión:** 1.0 — MVP

---

## 1. Stack Tecnológico

### Backend
| Componente | Tecnología | Razón |
|---|---|---|
| Lenguaje | Python 3.11+ | Mejor ecosistema para IA/audio |
| Framework web | FastAPI | Rápido, tipado, OpenAPI automático |
| ORM | SQLAlchemy 2.0 + Alembic | Estándar de la industria, migraciones |
| Validación | Pydantic v2 | Integrado con FastAPI |
| Cola de tareas | Celery + Redis | Procesamiento asíncrono de audios |
| Base de datos | PostgreSQL 15 | Confiable, escalable, JSON nativo |
| Storage de audios | Amazon S3 (o Railway Volumes en MVP) | Persistencia de archivos |
| Auth | JWT (python-jose) + bcrypt | Estándar, sin dependencias externas |

### Frontend
| Componente | Tecnología | Razón |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR/SSG, TypeScript, Vercel-friendly |
| UI library | shadcn/ui + Tailwind CSS | Moderno, accesible, customizable |
| Charts | Recharts | Ligero, integra bien con React |
| HTTP client | Axios + TanStack Query | Caching y revalidación automática |
| Forms | React Hook Form + Zod | Validación tipada |
| State | Zustand | Simple, sin boilerplate de Redux |

### Servicios externos
| Servicio | Uso | Costo aprox |
|---|---|---|
| **Groq API** | Transcripción (Whisper) | Gratis hasta cuota, luego $0.04/hora audio |
| **Anthropic Claude API** | Análisis de transcripción | ~$0.01-0.03 por llamada |
| **OpenAI API** (alternativa) | Análisis (configurable) | ~$0.01-0.03 por llamada |
| **Resend** (opcional) | Envío de emails | Gratis hasta 100/día |

### Infraestructura
| Componente | Plataforma | Costo |
|---|---|---|
| Backend hosting | Railway | ~$5-10/mes |
| Frontend hosting | Vercel | Gratis (Hobby tier) |
| Base de datos | Railway PostgreSQL | Incluido en plan |
| Redis | Railway Redis | ~$5/mes |
| Storage de audios | Railway Volume o AWS S3 | Incluido / ~$1/mes |

**Costo total estimado MVP:** ~$10-20/mes

---

## 2. Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                          USUARIO (Supervisor)                    │
│                       Browser (Chrome/Edge)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND (Vercel)                          │
│                    Next.js 14 + Tailwind                         │
│                  https://callqa.vercel.app                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (Railway)                          │
│                    FastAPI + Python 3.11                         │
│                 https://api-callqa.railway.app                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Auth (JWT) │ Llamadas │ Ejecutivos │ Dashboard │ Conf  │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────┬─────────────────┬──────────────────┬────────────────────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌──────────────┐  ┌────────────┐  ┌──────────────────────────┐
│ PostgreSQL   │  │   Redis    │  │  Celery Workers          │
│ (Railway)    │  │  (cola)    │  │  - Transcripción         │
│              │  │            │  │  - Análisis IA           │
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
│              Railway Volume (MVP) o AWS S3                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Flujo de Procesamiento de una Llamada

```
1. Supervisor sube audio vía frontend
   └─► POST /api/calls (multipart/form-data)
        │
        ├─► Backend guarda archivo en storage
        ├─► Crea registro en BD con status="QUEUED"
        ├─► Encola tarea en Celery
        └─► Responde 202 Accepted con call_id

2. Celery worker toma la tarea
        │
        ├─► Marca status="TRANSCRIBING"
        ├─► Descarga audio del storage
        ├─► Envía a Groq API (Whisper)
        ├─► Guarda transcripción en BD
        └─► Marca status="ANALYZING"

3. Celery worker continúa con análisis
        │
        ├─► Enmascara datos sensibles (regex)
        ├─► Construye prompt con la rúbrica + transcripción
        ├─► Envía a Claude/GPT API
        ├─► Parsea respuesta JSON (scores + recomendaciones)
        ├─► Guarda análisis en BD
        └─► Marca status="DONE"

4. Frontend hace polling cada 5 segundos
        │
        └─► GET /api/calls/{id}/status
             Cuando status="DONE", redirige al detalle
```

---

## 4. Modelo de Datos

### Diagrama entidad-relación

```
┌──────────────────┐         ┌──────────────────┐
│      users       │         │     agents       │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ email (unique)   │         │ name             │
│ password_hash    │         │ email            │
│ name             │         │ campaign         │
│ role             │         │ start_date       │
│ created_at       │         │ active           │
└──────────────────┘         │ created_at       │
                             └────────┬─────────┘
                                      │
                                      │ 1:N
                                      ▼
                             ┌──────────────────────┐
                             │       calls          │
                             ├──────────────────────┤
                             │ id (PK)              │
                             │ agent_id (FK)        │
                             │ uploaded_by (FK)     │
                             │ audio_url            │
                             │ duration_seconds     │
                             │ language             │
                             │ status (enum)        │
                             │ call_date            │
                             │ campaign_type        │
                             │ call_reason          │
                             │ error_message        │
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
                │ created_at       │          │ ai_provider          │
                └──────────────────┘          │ created_at           │
                                              └──────────────────────┘

┌──────────────────────┐
│  rubric_config       │
├──────────────────────┤
│ id (PK)              │
│ dimension_key        │
│ dimension_name       │
│ description          │
│ weight (decimal)     │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│   app_settings       │
├──────────────────────┤
│ key (PK)             │
│ value                │
│ updated_at           │
└──────────────────────┘
```

### Definición de tablas (SQL)

```sql
-- Usuarios del sistema (supervisores QA)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'supervisor',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Ejecutivos evaluados (no son usuarios del sistema)
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

-- Llamadas subidas para análisis
CREATE TYPE call_status AS ENUM ('QUEUED', 'TRANSCRIBING', 'ANALYZING', 'DONE', 'ERROR');

CREATE TABLE calls (
    id SERIAL PRIMARY KEY,
    agent_id INT NOT NULL REFERENCES agents(id),
    uploaded_by INT NOT NULL REFERENCES users(id),
    audio_url VARCHAR(500) NOT NULL,
    audio_filename VARCHAR(255),
    duration_seconds INT,
    file_size_bytes BIGINT,
    language VARCHAR(10) DEFAULT 'es',
    status call_status DEFAULT 'QUEUED',
    call_date DATE,
    campaign_type VARCHAR(100),
    call_reason TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

CREATE INDEX idx_calls_agent ON calls(agent_id);
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
    ai_provider VARCHAR(50),  -- 'claude' o 'openai'
    ai_model VARCHAR(100),
    tokens_used INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Configuración de la rúbrica
CREATE TABLE rubric_config (
    id SERIAL PRIMARY KEY,
    dimension_key VARCHAR(50) UNIQUE NOT NULL,
    dimension_name VARCHAR(255) NOT NULL,
    description TEXT,
    weight DECIMAL(5,2) NOT NULL,  -- Suma de pesos = 100.00
    display_order INT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Settings globales (idioma, proveedor IA, etc.)
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
('ai_provider', 'claude'),
('whisper_provider', 'groq');
```

---

## 5. API Contracts (Endpoints REST)

### Convenciones generales

- Base URL: `https://api-callqa.railway.app/api/v1`
- Autenticación: `Authorization: Bearer <JWT>` en todos los endpoints excepto `/auth/*`
- Formato: JSON
- Códigos de respuesta estándar HTTP

### Autenticación

#### POST `/auth/login`
**Body:**
```json
{ "email": "supervisor@banco.com", "password": "..." }
```
**Respuesta 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": { "id": 1, "name": "Juan Pérez", "email": "..." }
}
```

#### POST `/auth/refresh`
**Respuesta 200:** Nuevo access token

#### POST `/auth/logout`
**Respuesta 204**

---

### Ejecutivos

#### GET `/agents`
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

#### POST `/agents`
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

#### GET `/agents/{id}`
**Respuesta 200:** Detalle del agente + estadísticas (score promedio, total de llamadas)

#### PUT `/agents/{id}`
**Body:** Campos a actualizar
**Respuesta 200:** Objeto actualizado

#### DELETE `/agents/{id}` (soft delete)
**Respuesta 204**

---

### Llamadas

#### POST `/calls`
**Body (multipart/form-data):**
- `audio`: archivo de audio
- `agent_id`: int
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

#### POST `/calls/batch`
**Body (multipart/form-data):** múltiples archivos
**Respuesta 202:** lista de IDs creados

#### GET `/calls`
**Query params:**
- `agent_id`: int (opcional)
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

#### GET `/calls/{id}`
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

#### GET `/calls/{id}/status`
**Respuesta 200:** Solo el status (para polling rápido)
```json
{ "id": 123, "status": "ANALYZING", "progress_percent": 65 }
```

#### POST `/calls/{id}/retry`
**Respuesta 202**

#### GET `/calls/{id}/report.pdf`
**Respuesta 200:** Archivo PDF binario

#### DELETE `/calls/{id}`
**Respuesta 204**

---

### Dashboard

#### GET `/dashboard/summary`
**Query params:** `?period=30d` (7d, 30d, 90d)
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

#### GET `/dashboard/agents/{id}`
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
**Respuesta 200:** Array de dimensiones con pesos

#### PUT `/config/rubric`
**Body:** Array con `dimension_key` y `weight` (suma = 100)
**Respuesta 200**

#### GET `/config/settings`
**Respuesta 200:**
```json
{ "default_language": "es", "ai_provider": "claude" }
```

#### PUT `/config/settings`
**Body:** Objeto con configs a actualizar
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
│   ├── dependencies.py         # FastAPI dependencies (auth, db)
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── agent.py
│   │   ├── call.py
│   │   ├── transcription.py
│   │   ├── analysis.py
│   │   └── config.py
│   │
│   ├── schemas/                # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── agent.py
│   │   ├── call.py
│   │   ├── analysis.py
│   │   └── dashboard.py
│   │
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── agents.py
│   │   ├── calls.py
│   │   ├── dashboard.py
│   │   └── config.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── agent_service.py
│   │   ├── call_service.py
│   │   ├── storage_service.py  # S3 / Railway Volume
│   │   ├── transcription_service.py  # Groq / Whisper local
│   │   ├── analysis_service.py       # Claude / OpenAI
│   │   ├── pdf_service.py
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
├── alembic/                    # Migraciones DB
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_calls.py
│   └── test_analysis.py
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
│   ├── page.tsx                # Landing / redirect a login
│   ├── login/page.tsx
│   ├── dashboard/page.tsx
│   ├── calls/
│   │   ├── page.tsx            # Listado
│   │   ├── new/page.tsx        # Subida
│   │   └── [id]/page.tsx       # Detalle
│   ├── agents/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   ├── settings/
│   │   └── page.tsx
│   └── api/                    # Next.js API routes (opcional)
│
├── components/
│   ├── ui/                     # shadcn components
│   ├── layout/                 # Sidebar, Header
│   ├── calls/                  # CallTable, CallDetail, UploadForm
│   ├── dashboard/              # KPICards, Charts
│   └── shared/                 # Loaders, ErrorBoundary
│
├── lib/
│   ├── api.ts                  # Axios instance
│   ├── auth.ts                 # Auth helpers
│   ├── queries.ts              # TanStack Query hooks
│   └── utils.ts
│
├── types/                      # TypeScript types
├── public/
├── .env.local.example
├── next.config.js
├── tailwind.config.ts
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
AI_PROVIDER=claude      # claude | openai | azure
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
CORS_ORIGINS=https://callqa.vercel.app,http://localhost:3000
```

### Frontend `.env.local.example`

```bash
NEXT_PUBLIC_API_URL=https://api-callqa.railway.app/api/v1
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
| HTTPS | Forzado en producción (Railway/Vercel lo manejan) |
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

Las migraciones se ejecutan automáticamente al desplegar en Railway mediante un comando en el `Dockerfile` o `release_command` en `railway.json`.
