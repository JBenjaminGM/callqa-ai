# 🎧 CallQA AI

Plataforma de **Quality Assurance automatizado con IA** para call centers
bancarios (Minsait / Grupo Indra). Monorepo: backend + frontend + documentación.

> ⚠️ **Prototipo / demo interna.** No usar con datos reales de clientes.

- 🌐 **En vivo:** https://callqa-ai.vercel.app · API: https://callqa-api.onrender.com
- 👤 **Acceso demo:** `admin@callqa.com` / `Admin123!`
- 🤖 **¿Eres una IA o un dev nuevo?** → **[`docs/AGENTS.md`](docs/AGENTS.md)** (guía completa).
- 📚 **Toda la documentación está en [`docs/`](docs/)** (índice: [`docs/00_INDICE.md`](docs/00_INDICE.md)).

---

## 🚀 Arranque rápido (local)

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

## 📂 Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `backend/` | API FastAPI (+ worker Celery en local) — Python |
| `frontend/` | App web Next.js 14 (TypeScript) |
| **`docs/`** | **Toda la documentación** (guía `AGENTS.md`, estado, changelog, despliegue, diseño, pitch…) |
| `docker-compose.yml` · `render.yaml` | Config: stack local / blueprint de Render |

---

## 🛠️ Desarrollo y despliegue

- **Tests backend (33):** `cd backend && .venv\Scripts\python -m pytest -q`.
- **Frontend en local:** `cd frontend && npm install && npm run dev`.
- **Desplegar:** `git push origin main` → Vercel y Render redepliegan solos. Guía: **[`docs/DEPLOY_GRATIS.md`](docs/DEPLOY_GRATIS.md)**.

Para el detalle completo del estado y cómo trabajar, lee **[`docs/AGENTS.md`](docs/AGENTS.md)**.
