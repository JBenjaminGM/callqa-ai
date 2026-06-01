# 🎧 CallQA AI — Backend

Backend del **prototipo** de Quality Assurance automatizado para call centers
bancarios. Permite subir grabaciones de llamadas, transcribirlas con IA y
evaluarlas automáticamente contra una rúbrica editable (7 dimensiones por
defecto, con subcategorías activables).

> ⚠️ **PROTOTIPO — DEMO INTERNA.** Esta es una prueba de concepto. No utilizar
> con datos reales de clientes sin aprobación previa de Compliance.

---

## 1. ¿Qué es esto?

Es una API REST construida con **Python + FastAPI** que:

1. Recibe archivos de audio (MP3, WAV, M4A, OGG, FLAC).
2. Los transcribe usando **Groq (Whisper)**.
3. Analiza la transcripción con **Groq (Llama 3.3 70B) por defecto**, con
   **Claude (Anthropic)**, **GPT (OpenAI)** o **Azure** como opciones.
4. Devuelve scores por dimensión, un score global y recomendaciones.

El procesamiento pesado se hace en segundo plano con **Celery + Redis**, así la
API responde de inmediato y el frontend consulta el estado por *polling*.

---

## 2. Requisitos previos

| Herramienta | Para qué | Descarga |
|---|---|---|
| Docker Desktop | Ejecutar todo el sistema localmente | https://www.docker.com/products/docker-desktop/ |
| Cuenta en Groq | API de transcripción | https://console.groq.com |
| Cuenta en Anthropic | API de análisis IA | https://console.anthropic.com |

No necesitas instalar Python ni PostgreSQL: Docker se encarga de todo.

---

## 3. Cómo obtener las API keys

### Groq (transcripción)

1. Entra a https://console.groq.com/ e inicia sesión.
2. Menú lateral → **API Keys** → **Create API Key**.
3. Copia la clave (empieza por `gsk_...`). **No se vuelve a mostrar.**

### Anthropic (análisis IA)

1. Entra a https://console.anthropic.com/ y crea una cuenta.
2. Añade un método de pago (solo se cobra el uso real, ~$0.02 por llamada).
3. **API Keys** → **Create Key**. Copia la clave (empieza por `sk-ant-...`).

### OpenAI (opcional)

Solo si quieres poder alternar a GPT. https://platform.openai.com/api-keys

---

## 4. Configuración local (paso a paso)

```bash
# 1. Sitúate en la carpeta del proyecto
cd callqa-backend

# 2. Copia el archivo de ejemplo de variables de entorno
#    En Windows (PowerShell):  Copy-Item .env.example .env
cp .env.example .env

# 3. Edita .env y rellena al menos estas claves:
#    GROQ_API_KEY=gsk_...
#    ANTHROPIC_API_KEY=sk-ant-...
#    JWT_SECRET=algo-largo-y-aleatorio

# 4. Levanta todo el sistema
docker-compose up
```

Espera ~2 minutos. Cuando veas `Application startup complete`, abre:

- **http://localhost:8000/docs** → documentación interactiva de la API.

El arranque ejecuta automáticamente las migraciones y el *seed* de datos.

### Credenciales de demo

- Usuario: `admin@callqa.com`
- Contraseña: `Admin123!`

---

## 5. Cómo desplegar en Railway

1. Sube este repositorio a GitHub (privado recomendado).
2. En https://railway.app → **New Project → Deploy from GitHub repo**.
3. Añade los servicios de base de datos:
   - **+ New → Database → Add PostgreSQL**
   - **+ New → Database → Add Redis**
4. En el servicio del backend, pestaña **Variables**, configura:

   ```
   GROQ_API_KEY=gsk_...
   AI_PROVIDER=groq
   WHISPER_PROVIDER=groq
   # ANTHROPIC_API_KEY=sk-ant-...   # solo si usas AI_PROVIDER=claude (de pago)
   JWT_SECRET=cadena-larga-aleatoria
   APP_ENV=production
   STORAGE_PROVIDER=local
   STORAGE_PATH=/data/audios
   CORS_ORIGINS=https://tu-frontend.vercel.app
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

5. **Settings → Volumes**: añade un volumen montado en `/data` (1 GB).
6. Crea un segundo servicio (**Empty Service**) para el worker de Celery:
   - Mismo repositorio.
   - Start Command: `celery -A app.tasks.celery_app worker --loglevel=info`
   - Mismas variables de entorno y el mismo volumen `/data`.
7. **Settings → Networking → Generate Domain** para obtener la URL pública.
8. Verifica en `https://tu-backend.up.railway.app/docs`.
9. Carga los datos iniciales ejecutando `python scripts/seed_data.py` desde la
   shell de Railway (o se ejecuta solo si usas el comando de arranque local).

---

## 6. Estructura del proyecto

```
callqa-backend/
├── app/
│   ├── main.py            # Arranque de FastAPI, CORS, logging, routers
│   ├── config.py          # Configuración leída de variables de entorno
│   ├── database.py        # Conexión a PostgreSQL
│   ├── dependencies.py    # Autenticación JWT
│   ├── limiter.py         # Rate limiting compartido
│   ├── models/            # Tablas de la base de datos (SQLAlchemy)
│   ├── schemas/           # Validación de entrada/salida (Pydantic)
│   ├── routers/           # Endpoints de la API
│   ├── services/          # Lógica de negocio (IA, storage, PDF, etc.)
│   ├── tasks/             # Tareas Celery (procesamiento asíncrono)
│   ├── prompts/           # Prompts para los modelos de lenguaje
│   └── utils/             # Seguridad y validación de audio
├── alembic/               # Migraciones de la base de datos
├── scripts/seed_data.py   # Datos iniciales (admin, rúbrica, ejecutivos)
├── tests/                 # Tests automatizados
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 7. Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/auth/login` | Iniciar sesión, obtener token JWT |
| GET | `/api/v1/auth/me` | Datos del usuario autenticado |
| GET / POST | `/api/v1/agents` | Listar / crear ejecutivos |
| PUT / DELETE | `/api/v1/agents/{id}` | Editar / desactivar ejecutivo |
| POST | `/api/v1/calls` | Subir un audio para análisis |
| POST | `/api/v1/calls/batch` | Subir varios audios |
| GET | `/api/v1/calls` | Listado paginado de llamadas |
| GET | `/api/v1/calls/{id}` | Detalle (transcripción + análisis) |
| GET | `/api/v1/calls/{id}/status` | Estado del procesamiento (polling) |
| POST | `/api/v1/calls/{id}/retry` | Reintentar una llamada con error |
| GET | `/api/v1/calls/{id}/report.pdf` | Descargar reporte PDF |
| GET | `/api/v1/dashboard/summary` | KPIs agregados del equipo |
| GET | `/api/v1/dashboard/agents/{id}` | Performance de un ejecutivo |
| GET / PUT | `/api/v1/config/rubric` | Consultar / ajustar la rúbrica |
| GET / PUT | `/api/v1/config/settings` | Consultar / cambiar settings |

Todos los endpoints (excepto `/auth/*`) requieren la cabecera
`Authorization: Bearer <token>`.

---

## 8. Ejecutar los tests

```bash
# Dentro del contenedor de la API
docker-compose run --rm api pytest

# O en local, con un entorno virtual de Python:
pip install -r requirements.txt
pytest
```

Los tests usan SQLite en memoria y no necesitan PostgreSQL ni claves de API.

---

## 9. Solución de problemas comunes

| Problema | Solución |
|---|---|
| `docker-compose up` falla al construir | Verifica que Docker Desktop esté corriendo. |
| La llamada se queda en `TRANSCRIBING` | Revisa que el servicio `worker` esté activo y que `GROQ_API_KEY` sea válida. |
| `Invalid API key` de Anthropic | La clave debe empezar por `sk-ant-` y tu cuenta debe tener saldo. |
| Error de CORS desde el frontend | Añade la URL exacta del frontend a `CORS_ORIGINS` (sin barra final). |
| El audio no se sube | Verifica formato (MP3/WAV/M4A/OGG/FLAC) y tamaño (≤ 100 MB). |

---

## 10. Notas sobre portabilidad (contexto Minsait/Indra)

El código está preparado para migrar a infraestructura Azure sin reescribirse:

- Los proveedores de IA y transcripción usan **patrón factory**: basta cambiar
  las variables `AI_PROVIDER` / `WHISPER_PROVIDER` para alternar entre
  Claude, OpenAI, Azure OpenAI y Azure Speech.
- Toda la configuración vive en variables de entorno.
- Cada respuesta incluye el header `X-Prototype-Notice` y los logs llevan el
  campo `environment: prototype` para auditoría.
