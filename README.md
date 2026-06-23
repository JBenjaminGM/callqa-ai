# 🎧 CallQA AI

Plataforma de **Quality Assurance automatizado con IA** para call centers
bancarios (Minsait / Grupo Indra). Monorepo: backend + frontend + documentación.

> ⚠️ **Vista previa — entorno de evaluación.** No utilizar con datos reales de
> clientes sin la aprobación previa de Compliance.

- 🌐 **En vivo:** https://callqa-ai.vercel.app · API: https://callqa-api.onrender.com
- 👤 **Roles:** `admin@callqa.com` / `Admin123!` (admin) · `jefe@callqa.com` / `Jefe123!` (jefe) · asesores con el email del ejecutivo (p. ej. `maria@banco.com` / `Asesor123!`).
- 🤖 **¿Eres una IA o un dev nuevo?** → **[`docs/AGENTS.md`](docs/AGENTS.md)** (guía completa).
- 📚 **Toda la documentación está en [`docs/`](docs/)** (índice: [`docs/00_INDICE.md`](docs/00_INDICE.md)).

---

## 🚀 Arranque rápido (Local)

Requisito: **Docker Desktop** abierto + una **API key de Groq** (gratis) en `backend/.env`.

```bash
cd callqa-ai
docker compose up --build
```
- 🖥️ App: <http://localhost:3000>  ·  📚 API: <http://localhost:8000/docs>  ·  Detener: `docker compose down`.

### Activar la IA (gratis, $0)
En `backend/.env` basta una clave de **Groq** (hace transcripción **y** análisis):
```
GROQ_API_KEY=gsk_...
AI_PROVIDER=groq
WHISPER_PROVIDER=groq
```
> Claude / OpenAI / Azure son opcionales (de pago): cambia `AI_PROVIDER` y pon su API key.

---

## ✨ Qué hace

Sube audios → transcribe (Groq Whisper large v3) → enmascara PII (best-effort) →
analiza con LLM (Groq Llama 3.3 70B) contra una **rúbrica dinámica** → scores por
dimensión + score global ponderado + recomendaciones accionables + **reporte PDF**.

- **Roles:** `admin` y `jefe` (mismos permisos: gestión + analítica global) y
  `asesor` (solo su propio rendimiento, su ficha y sus llamadas).
- **Campañas con nota de producto:** cada campaña lleva una ficha de oferta (9
  campos) que la IA usa para evaluar si el ejecutivo ofreció lo correcto. Se crea
  por formulario, con asistente IA, o subiendo un PDF que la IA parsea.
- **Umbrales QA configurables:** objetivo, alertas de asesor/llamada y ranking,
  editables por el jefe.
- **Identidad Minsait:** paleta Pruno + Gris Cerámica con acento Fucsia,
  tipografía ForFuture Sans y contenedores achaflanados.

---

## 📂 Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `backend/` | API FastAPI (+ worker Celery en local) — Python |
| `frontend/` | App web Next.js 14 (TypeScript) |
| **`docs/`** | **Toda la documentación** (guía `AGENTS.md`, estado, changelog, despliegue, diseño, pitch…) |
| `docker-compose.yml` · `render.yaml` | Config: stack local / blueprint de Render |

---

## 🛠️ Desarrollo y despliegue

- **Tests backend (61):** `cd backend && .venv\Scripts\python -m pytest -q`.
- **Frontend en local:** `cd frontend && npm install && npm run dev`.
- **Desplegar:** `git push origin main` → Vercel y Render redepliegan solos. Guía: **[`docs/DEPLOY_GRATIS.md`](docs/DEPLOY_GRATIS.md)**.

Para el detalle completo del estado y cómo trabajar, lee **[`docs/AGENTS.md`](docs/AGENTS.md)**.
