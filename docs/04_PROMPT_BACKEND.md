# 🤖 PROMPT MAESTRO PARA CLAUDE CODE — BACKEND

> 📌 **Documento histórico.** Este es el prompt maestro con el que se generó el backend. El proyecto evolucionó desde entonces (Groq por defecto en vez de Claude, rúbrica con subcategorías, diarización por LLM, paleta Índigo, etc.). Para el estado REAL ver `ESTADO_DEL_PROYECTO.md`.

> **Instrucciones de uso:**
> 1. Abre Claude Code en una carpeta vacía llamada `callqa-backend`
> 2. Copia y pega TODO este prompt en una sola conversación
> 3. Claude Code generará todos los archivos del backend
> 4. Sigue después la guía de despliegue (`05_GUIA_DESPLIEGUE.md`)

---

## INICIO DEL PROMPT (copiar desde aquí)

```
Eres un desarrollador senior Python especializado en FastAPI y sistemas de IA aplicada. Vas a construir el backend completo de "CallQA AI", una plataforma de Quality Assurance automatizado para call centers bancarios. Quien te da instrucciones NO es desarrollador, así que prioriza:

1. Código limpio, comentado en español, fácil de entender y mantener.
2. Configuración out-of-the-box: que funcione con `docker-compose up` sin pasos extra.
3. Mensajes de error claros en español orientados a usuarios no técnicos.
4. README detallado con instrucciones paso a paso.
5. Despliegue listo para Railway (con archivos de configuración específicos).

═══════════════════════════════════════════════════════════════════
CONTEXTO DEL PROYECTO
═══════════════════════════════════════════════════════════════════

CallQA AI permite a supervisores de QA de un call center bancario subir grabaciones de llamadas (MP3, WAV, M4A) y obtener automáticamente:
- Transcripción con timestamps y diarización (quién habla)
- Análisis IA sobre 7 dimensiones (saludo, asertividad, promociones, normativa, resolución, objeciones, sentimiento)
- Score global 0-100 tipo NPS
- Recomendaciones accionables para el ejecutivo
- Comparativas contra el promedio del equipo

Usuario: un único rol "supervisor" en el MVP.

CONTEXTO ORGANIZACIONAL IMPORTANTE:
- Es un PROTOTIPO/PoC interno para Minsait (Grupo Indra) — sector banca.
- En esta fase NO se procesarán datos reales de clientes (audios simulados/sintéticos).
- A futuro podría migrar a Azure (Azure OpenAI, Azure Speech). Por eso el código DEBE ser portable: factory patterns para proveedores de IA y transcripción, configuración 100% por variables de entorno.
- En todos los endpoints, devolver un header `X-Prototype-Notice: This is a prototype - Do not use with real customer data` para reforzar el contexto.
- Logs deben incluir un campo `environment: prototype` para auditoría.

═══════════════════════════════════════════════════════════════════
STACK TECNOLÓGICO (USAR EXACTAMENTE ESTO)
═══════════════════════════════════════════════════════════════════

- Python 3.11
- FastAPI (última estable)
- SQLAlchemy 2.0 con sintaxis moderna (DeclarativeBase, Mapped, mapped_column)
- Alembic para migraciones
- PostgreSQL 15
- Redis 7
- Celery 5 (worker para procesamiento asíncrono)
- Pydantic v2 (Settings y schemas)
- python-jose[cryptography] para JWT
- passlib[bcrypt] para hashing de contraseñas
- httpx para llamadas a APIs externas (Groq, Claude, OpenAI)
- python-multipart para uploads
- reportlab para generación de PDFs
- pytest + pytest-asyncio para tests

APIs externas a integrar:
- Groq API para transcripción Whisper (https://api.groq.com/openai/v1/audio/transcriptions)
- Anthropic API para análisis (modelo: claude-sonnet-4-6)
- OpenAI API como alternativa (modelo: gpt-4o)
- Configurable vía variable AI_PROVIDER=claude|openai

═══════════════════════════════════════════════════════════════════
ESTRUCTURA DE CARPETAS A GENERAR
═══════════════════════════════════════════════════════════════════

callqa-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── agent.py
│   │   ├── call.py
│   │   ├── transcription.py
│   │   ├── analysis.py
│   │   └── settings.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── agent.py
│   │   ├── call.py
│   │   ├── analysis.py
│   │   ├── dashboard.py
│   │   └── config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── agents.py
│   │   ├── calls.py
│   │   ├── dashboard.py
│   │   └── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── agent_service.py
│   │   ├── call_service.py
│   │   ├── storage_service.py
│   │   ├── transcription_service.py
│   │   ├── analysis_service.py
│   │   ├── pdf_service.py
│   │   └── masking_service.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── call_tasks.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── analysis_es.py
│   │   └── analysis_en.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       └── audio.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_agents.py
│   └── test_calls.py
├── scripts/
│   └── seed_data.py
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── railway.json
├── Procfile
└── README.md

═══════════════════════════════════════════════════════════════════
MODELO DE DATOS (SQLAlchemy 2.0 con sintaxis Mapped)
═══════════════════════════════════════════════════════════════════

Implementa estos modelos exactamente:

1. User: id, email (unique), password_hash, name, role (default 'supervisor'), created_at, last_login
2. Agent: id, name, email, campaign, start_date, active (default True), photo_url, created_at, updated_at
3. Call: id, agent_id (FK), uploaded_by (FK users), audio_url, audio_filename, duration_seconds, file_size_bytes, language (default 'es'), status (Enum: QUEUED, TRANSCRIBING, ANALYZING, DONE, ERROR), call_date, campaign_type, call_reason, error_message, created_at, processed_at
4. Transcription: id, call_id (FK unique), full_text, segments (JSONB), language, created_at
5. Analysis: id, call_id (FK unique), global_score (0-100), dimension_scores (JSONB), recommendations (JSONB), summary (text), ai_provider, ai_model, tokens_used, created_at
6. RubricConfig: id, dimension_key (unique), dimension_name, description, weight (decimal), display_order, updated_at
7. AppSettings: key (PK), value, updated_at

Crea la migración inicial con Alembic. Crea un script `seed_data.py` que:
- Inserte un usuario admin (email: admin@callqa.com, password: Admin123!)
- Inserte las 7 dimensiones de la rúbrica con pesos iguales (14.28% c/u, la última 14.32%)
- Inserte settings por defecto: default_language='es', ai_provider='claude', whisper_provider='groq'
- Inserte 3 ejecutivos de ejemplo

═══════════════════════════════════════════════════════════════════
ENDPOINTS DE LA API (todos bajo /api/v1)
═══════════════════════════════════════════════════════════════════

AUTH (sin auth requerida)
- POST /auth/login → recibe email + password, devuelve JWT
- POST /auth/refresh → renueva token
- POST /auth/logout → invalida token (puede ser solo respuesta 204)
- GET /auth/me → devuelve usuario autenticado

AGENTS (requiere auth)
- GET /agents?active=true&search= → lista de ejecutivos
- POST /agents → crear ejecutivo
- GET /agents/{id} → detalle + estadísticas (total llamadas, score promedio)
- PUT /agents/{id} → editar
- DELETE /agents/{id} → soft delete (active=false)

CALLS (requiere auth)
- POST /calls → multipart/form-data: audio + agent_id + metadatos opcionales. Encola tarea Celery, devuelve 202 con call_id
- POST /calls/batch → múltiples archivos
- GET /calls → listado paginado con filtros (agent_id, status, fechas, scores)
- GET /calls/{id} → detalle completo (call + transcription + analysis + team_average)
- GET /calls/{id}/status → solo status (para polling)
- POST /calls/{id}/retry → reintentar procesamiento
- GET /calls/{id}/report.pdf → descargar PDF del reporte
- DELETE /calls/{id} → eliminar

DASHBOARD (requiere auth)
- GET /dashboard/summary?period=30d → KPIs agregados del equipo
- GET /dashboard/agents/{id}?period=30d → performance del ejecutivo

CONFIG (requiere auth)
- GET /config/rubric → rúbrica actual
- PUT /config/rubric → actualizar pesos (validar suma = 100)
- GET /config/settings → settings actuales
- PUT /config/settings → actualizar settings

═══════════════════════════════════════════════════════════════════
FLUJO DE PROCESAMIENTO (TAREA CELERY)
═══════════════════════════════════════════════════════════════════

Cuando se sube una llamada:

1. El endpoint POST /calls:
   - Valida formato (MP3, WAV, M4A, OGG, FLAC) y tamaño (≤100MB)
   - Sube el archivo a storage (local o S3 según config)
   - Crea registro en BD con status=QUEUED
   - Dispara tarea Celery `process_call(call_id)`
   - Responde 202

2. La tarea Celery `process_call(call_id)`:
   a) Actualiza status=TRANSCRIBING
   b) Descarga audio desde storage
   c) Llama a Groq API (Whisper):
      - Endpoint: https://api.groq.com/openai/v1/audio/transcriptions
      - Modelo: whisper-large-v3
      - response_format: verbose_json (para obtener segments con timestamps)
   d) Si Groq no soporta diarización nativa, usar heurística: alternar speaker_a/speaker_b por turnos detectados por pausas largas. Marcar el primer turno como "agent" (es el ejecutivo quien saluda).
   e) Guarda transcription en BD
   f) Actualiza status=ANALYZING
   g) Enmascara datos sensibles en la transcripción (regex de tarjetas: \d{13,19}, DNI peruano: \d{8}, CVV: \d{3,4})
   h) Llama al servicio de análisis (Claude o GPT según config):
      - Construye prompt usando `app/prompts/analysis_es.py` (incluir la rúbrica con sus 7 dimensiones)
      - Solicita salida en JSON estructurado
      - Parsea la respuesta
   i) Guarda analysis en BD
   j) Actualiza status=DONE, processed_at=now()

Si falla en cualquier punto: status=ERROR, error_message con detalle. Permitir reintento.

═══════════════════════════════════════════════════════════════════
PROMPT DE ANÁLISIS (ARCHIVO app/prompts/analysis_es.py)
═══════════════════════════════════════════════════════════════════

Crea una función `build_analysis_prompt(transcription_text, rubric)` que genere un prompt como este:

"""
Eres un experto en Quality Assurance de call centers bancarios. Vas a evaluar la siguiente llamada entre un EJECUTIVO del banco y un CLIENTE.

TRANSCRIPCIÓN DE LA LLAMADA:
{transcription_text}

RÚBRICA DE EVALUACIÓN (7 dimensiones, score 0-100 cada una):

1. SALUDO Y PROTOCOLO: ¿Saludó correctamente? ¿Se identificó? ¿Mencionó la grabación? ¿Cerró adecuadamente?
2. ASERTIVIDAD Y TONO: ¿Empático, claro, paciente? ¿Tono profesional? ¿Escuchó activamente?
3. MENCIÓN DE PROMOCIONES/PRODUCTOS: ¿Mencionó productos relevantes? ¿Explicó beneficios correctamente?
4. CUMPLIMIENTO NORMATIVO: ¿Mencionó disclaimers? ¿Protegió datos sensibles? ¿Pidió consentimiento?
5. RESOLUCIÓN: ¿Resolvió el motivo de la llamada? ¿Ofreció soluciones concretas?
6. MANEJO DE OBJECIONES: ¿Manejó bien las dudas/objeciones del cliente? ¿Persuasión profesional?
7. SENTIMIENTO DEL CLIENTE: ¿El cliente quedó satisfecho? (Inferir del tono, palabras, despedida)

INSTRUCCIONES:
- Sé objetivo y basa cada score en evidencia concreta de la transcripción.
- Genera 3-5 recomendaciones accionables priorizadas (high/medium/low).
- El resumen debe ser de 2-3 frases.

Responde EXCLUSIVAMENTE con un JSON válido con esta estructura exacta:

{
  "dimension_scores": {
    "greeting": <int 0-100>,
    "assertiveness": <int 0-100>,
    "promotions": <int 0-100>,
    "compliance": <int 0-100>,
    "resolution": <int 0-100>,
    "objections": <int 0-100>,
    "sentiment": <int 0-100>
  },
  "summary": "<resumen ejecutivo de la llamada>",
  "recommendations": [
    {
      "priority": "high|medium|low",
      "dimension": "<dimension_key>",
      "title": "<título corto>",
      "description": "<recomendación específica accionable>"
    }
  ]
}
"""

El score global se calcula en el backend (no en el LLM):
global_score = sum(dimension_scores[k] * rubric[k].weight / 100 for k in dimensions)
Redondeado a entero.

═══════════════════════════════════════════════════════════════════
SERVICIO DE ANÁLISIS (factory pattern)
═══════════════════════════════════════════════════════════════════

Crea `analysis_service.py` con un patrón factory que soporta 3 proveedores (importante para migración futura a Azure):

```python
class AnalysisProvider(ABC):
    @abstractmethod
    async def analyze(self, prompt: str) -> dict: ...

class ClaudeProvider(AnalysisProvider):
    # POST https://api.anthropic.com/v1/messages
    # Headers: x-api-key, anthropic-version: 2023-06-01, content-type
    # Body: {"model": "claude-sonnet-4-6", "max_tokens": 2000, "messages": [{"role": "user", "content": prompt}]}
    # Parsea response["content"][0]["text"] y extrae el JSON

class OpenAIProvider(AnalysisProvider):
    # POST https://api.openai.com/v1/chat/completions
    # response_format: {"type": "json_object"}
    # Modelo: gpt-4o

class AzureOpenAIProvider(AnalysisProvider):
    # Stub preparado para migración futura
    # POST https://{AZURE_OPENAI_ENDPOINT}/openai/deployments/{deployment}/chat/completions
    # Headers: api-key, content-type
    # Vars: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT
    # En MVP: implementar la estructura pero con NotImplementedError si no hay vars configuradas

def get_analysis_provider(settings) -> AnalysisProvider:
    if settings.ai_provider == "claude": return ClaudeProvider(...)
    if settings.ai_provider == "openai": return OpenAIProvider(...)
    if settings.ai_provider == "azure": return AzureOpenAIProvider(...)
    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
```

Ambos providers deben:
- Manejar timeouts (60s)
- Manejar rate limits con backoff exponencial (max 3 reintentos)
- Devolver dict parseado o lanzar excepción con mensaje claro
- Loggear tokens usados

═══════════════════════════════════════════════════════════════════
SERVICIO DE TRANSCRIPCIÓN
═══════════════════════════════════════════════════════════════════

Crea `transcription_service.py` con factory que soporta 3 proveedores:

```python
class TranscriptionProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str, language: str) -> dict: ...

class GroqProvider(TranscriptionProvider):
    # POST https://api.groq.com/openai/v1/audio/transcriptions
    # multipart/form-data con archivo
    # model: whisper-large-v3
    # response_format: verbose_json
    # language: código ISO (es, en, pt, etc.)
    # Devuelve: {"text": "...", "segments": [{"start", "end", "text"}, ...]}

class LocalWhisperProvider(TranscriptionProvider):
    # Stub para futuro: import whisper; whisper.load_model("medium")
    # En MVP: raise NotImplementedError("Whisper local no disponible en este deploy")

class AzureSpeechProvider(TranscriptionProvider):
    # Stub preparado para migración a Azure
    # Vars: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
    # En MVP: raise NotImplementedError si no hay vars configuradas
    # En el futuro: usar SDK azure-cognitiveservices-speech
```

Implementa una función `add_speaker_diarization(segments)` que asigna speakers basándose en pausas:
- Primer segmento: "agent"
- Si pausa entre segmentos > 1.5s, cambia speaker
- Alterna entre "agent" y "customer"

═══════════════════════════════════════════════════════════════════
SEGURIDAD
═══════════════════════════════════════════════════════════════════

- JWT con HS256, expiración configurable (default 8h)
- Bcrypt para passwords
- CORS habilitado para los orígenes en CORS_ORIGINS (lista separada por comas)
- Validación estricta con Pydantic v2 en TODOS los endpoints
- Rate limiting en /auth/login (5 intentos por IP en 15 min) usando slowapi
- Variables sensibles SOLO desde .env, nunca hardcoded
- Logs de operaciones críticas (login, creación de ejecutivos, errores de procesamiento)

═══════════════════════════════════════════════════════════════════
ENMASCARAMIENTO DE DATOS SENSIBLES
═══════════════════════════════════════════════════════════════════

En `services/masking_service.py`:

```python
import re

PATTERNS = {
    "card": (re.compile(r"\b\d{13,19}\b"), "[TARJETA]"),
    "dni_peru": (re.compile(r"\b\d{8}\b"), "[DNI]"),
    "cvv": (re.compile(r"\bcvv\s*:?\s*\d{3,4}\b", re.I), "cvv: [CVV]"),
    "phone": (re.compile(r"\b9\d{8}\b"), "[TELÉFONO]"),
}

def mask_sensitive_data(text: str) -> str:
    for pattern, replacement in PATTERNS.values():
        text = pattern.sub(replacement, text)
    return text
```

Aplica esto a la transcripción ANTES de enviarla al LLM para análisis.

═══════════════════════════════════════════════════════════════════
DOCKER Y RAILWAY
═══════════════════════════════════════════════════════════════════

Genera un Dockerfile multi-stage optimizado:
- Etapa builder: instala dependencias
- Etapa final: copia solo lo necesario, usuario no-root
- Comando: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2

Genera docker-compose.yml con servicios:
- api (FastAPI)
- worker (Celery)
- postgres
- redis

Genera railway.json:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "DOCKERFILE" },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

Genera Procfile (para Railway worker):
```
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A app.tasks.celery_app worker --loglevel=info
```

═══════════════════════════════════════════════════════════════════
TESTS MÍNIMOS
═══════════════════════════════════════════════════════════════════

Crea tests para:
- POST /auth/login (caso éxito y error)
- POST /agents (creación)
- GET /agents (listado)
- POST /calls con archivo dummy (mockear servicios externos)
- Cálculo del global_score
- Función mask_sensitive_data

Usa pytest fixtures para DB de tests (SQLite en memoria) y mocks para Groq/Claude.

═══════════════════════════════════════════════════════════════════
README.md DETALLADO
═══════════════════════════════════════════════════════════════════

El README debe incluir, en español y con tono didáctico para no-devs:

1. **¿Qué es esto?** — Descripción breve del proyecto
2. **Requisitos previos** — Docker Desktop, cuentas en Groq, Anthropic (con links)
3. **Cómo obtener las API keys** — Pasos para crear cuenta en Groq y Anthropic, dónde copiar la key
4. **Configuración local (paso a paso)**:
   - Clonar el repo
   - Copiar .env.example a .env y rellenar
   - `docker-compose up` 
   - Acceder a http://localhost:8000/docs
5. **Cómo desplegar en Railway**:
   - Crear cuenta
   - Conectar GitHub
   - Variables de entorno a configurar (lista exacta)
   - Cómo añadir PostgreSQL y Redis
6. **Estructura del proyecto** — Explicación de carpetas
7. **Endpoints principales** — Tabla resumen
8. **Solución de problemas comunes**

═══════════════════════════════════════════════════════════════════
INSTRUCCIONES FINALES PARA TI (CLAUDE CODE)
═══════════════════════════════════════════════════════════════════

1. Genera TODOS los archivos listados, sin omisiones.
2. Cada archivo Python debe ser FUNCIONAL y autocontenido, con imports correctos.
3. Usa type hints en TODO el código.
4. Comenta funciones complejas en español.
5. NO uses placeholders tipo "# TODO: implementar". Implementa todo.
6. Cuando termines, ejecuta `pytest` y asegúrate de que pasan todos los tests.
7. Cuando termines, ejecuta `docker-compose build` para verificar que el build funciona.
8. Al final, muestra al usuario:
   - Resumen de archivos creados
   - Próximos pasos (rellenar .env, ejecutar docker-compose up)
   - Cómo verificar que funciona (acceder a /docs)

Empieza ya. No me pidas confirmación de nada. Genera todo el proyecto completo.
```

## FIN DEL PROMPT (copiar hasta aquí)

---

## 📝 Notas importantes sobre el uso

### Antes de pegar el prompt en Claude Code:

1. **Tener API keys listas** (puedes obtenerlas gratis o con costo bajísimo):
   - **Groq:** https://console.groq.com/keys (gratis con generosos límites)
   - **Anthropic:** https://console.anthropic.com/settings/keys (~$5 USD de saldo inicial gratis a veces)
   - **OpenAI (opcional):** https://platform.openai.com/api-keys

2. **Tener Docker Desktop instalado** en tu computadora:
   - Mac: https://www.docker.com/products/docker-desktop/
   - Windows: igual link
   - Linux: `apt install docker.io docker-compose`

3. **Tener una cuenta de GitHub** (gratuita): https://github.com/signup

4. **Tener una cuenta en Railway** (gratuita): https://railway.app/

### Mientras Claude Code trabaja:

- Probablemente tarde **15-30 minutos** en generar todo
- Si en algún punto se detiene o falla algún archivo, simplemente dile: *"Continúa generando el resto de archivos"* o *"Hubo un error en X, regenera ese archivo"*
- No interrumpas el proceso a menos que veas un error claro

### Después de generar el código:

1. Sigue las instrucciones del archivo **`05_GUIA_DESPLIEGUE.md`**
2. Antes de desplegar en Railway, prueba localmente con `docker-compose up`
3. Si algo falla, copia el error y pégaselo a Claude Code para que lo arregle

### Si quieres iterar:

- Cuando algo no funcione como esperas, dile a Claude Code:
  > "El endpoint X devuelve Y, pero esperaba Z. Arréglalo."
- Para añadir features:
  > "Añade un endpoint para exportar todas las llamadas de un agente a Excel"

---

## 🎯 Resultado esperado

Al terminar este paso tendrás:

✅ Backend completo en Python/FastAPI
✅ Base de datos PostgreSQL con migraciones
✅ Procesamiento asíncrono con Celery
✅ Integración con Groq (transcripción) y Claude/GPT (análisis)
✅ API REST documentada automáticamente en `/docs`
✅ Listo para desplegar en Railway
✅ Tests básicos pasando
