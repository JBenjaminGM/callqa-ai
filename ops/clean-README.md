# CallQA AI

Plataforma web de **quality assurance automatizado** para call centers. Sube las
grabaciones de tus llamadas y la plataforma las transcribe, identifica al ejecutivo,
evalúa cada llamada contra una rúbrica configurable y te entrega paneles con
indicadores, alertas accionables y un reporte por llamada.

🌐 **Demo en vivo:** https://callqa-ai.vercel.app · API: https://callqa-api.onrender.com/docs

## Características

- **Transcripción y análisis automáticos** de cada llamada, con enmascarado
  *best-effort* de datos sensibles antes del análisis.
- **Rúbrica configurable** por dimensiones y subcriterios, con pesos.
- **Dashboards e indicadores**: score del equipo con su tendencia, distribución de
  scores, KPIs por campaña (con delta vs. periodo anterior), alertas accionables,
  ranking de ejecutivos y métricas de conversación (ratio hablar/escuchar, % de
  silencio, palabras por minuto, turnos).
- **Roles**: administrador / jefe de área (gestión y analítica global) y asesor
  (solo su propio rendimiento).
- **Campañas con nota de producto**: define la oferta que el ejecutivo debe presentar;
  la evaluación comprueba su cumplimiento (frases obligatorias, condiciones).
- **Reporte PDF** por llamada.

## Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL. Procesamiento
  con Celery + Redis (o inline para despliegues sin worker).
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, TanStack Query, Recharts.
- **Infra**: Docker Compose (stack completo en local); desplegable en Vercel (frontend)
  y Render (backend + PostgreSQL).

## Cómo correr en local

Requisito: Docker.

```bash
docker compose up -d --build
```

- Frontend: http://localhost:3000
- API + documentación: http://localhost:8000/docs

El arranque aplica las migraciones y crea usuarios de ejemplo (un administrador, un
jefe de área y asesores) junto con datos de demostración.

Para el análisis necesitas una clave de proveedor en `backend/.env` (el proveedor es
intercambiable: Groq, OpenAI, Claude o Azure):

```
AI_PROVIDER=groq
GROQ_API_KEY=...
```

## Estructura

```
backend/    API FastAPI: modelos, servicios, pipeline de procesamiento, migraciones y tests
frontend/   Aplicación Next.js: páginas, componentes y visualización de datos
```

## Tests

```bash
cd backend && python -m pytest -q
```

## Despliegue

`git push` a la rama principal → Vercel (frontend) y Render (backend + PostgreSQL)
redespliegan automáticamente. La configuración vive en `render.yaml` y `docker-compose.yml`.

## Licencia

Uso privado. Todos los derechos reservados.
