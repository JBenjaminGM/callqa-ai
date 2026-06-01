"""
Punto de entrada de la aplicación FastAPI de CallQA AI.

Configura CORS, logging estructurado, rate limiting, los routers de la API
y un middleware que añade el header de aviso de prototipo a cada respuesta.
"""

import json
import logging
import sys
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import agents, auth, calls, config, dashboard

# Aviso obligatorio del prototipo (contexto Minsait/Indra).
PROTOTYPE_NOTICE = "This is a prototype - Do not use with real customer data"


# --- Logging estructurado en JSON ---
class JsonFormatter(logging.Formatter):
    """Formatea cada log como una línea JSON con el campo environment=prototype."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": "prototype",
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)


def _configure_logging() -> None:
    """Configura el logging raíz para emitir JSON por stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


_configure_logging()
logger = logging.getLogger("callqa")

app = FastAPI(
    title="CallQA AI - API",
    description=(
        "Backend del prototipo de Quality Assurance automatizado para "
        "call centers bancarios. PROTOTIPO — no usar con datos reales de clientes."
    ),
    version="1.0.0-mvp",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: solo se permiten los orígenes definidos en la configuración.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Prototype-Notice"],
)


@app.middleware("http")
async def add_prototype_header(request: Request, call_next):
    """Añade el header de aviso de prototipo y loggea cada petición."""
    start = time.time()
    response = await call_next(request)
    response.headers["X-Prototype-Notice"] = PROTOTYPE_NOTICE
    elapsed_ms = round((time.time() - start) * 1000, 1)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Captura errores no controlados y devuelve un mensaje claro en español."""
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno. Inténtelo de nuevo más tarde."},
        headers={"X-Prototype-Notice": PROTOTYPE_NOTICE},
    )


@app.get("/", tags=["health"])
def root() -> dict:
    """Endpoint raíz: confirma que la API está viva."""
    return {
        "service": "CallQA AI",
        "status": "ok",
        "notice": PROTOTYPE_NOTICE,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health() -> dict:
    """Health check simple para Railway / monitorización."""
    return {"status": "healthy"}


# --- Registro de routers de la API (todos bajo /api/v1) ---
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(agents.router, prefix=API_PREFIX)
app.include_router(calls.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(config.router, prefix=API_PREFIX)
