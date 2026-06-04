# 🎧 CallQA AI

Plataforma de **Quality Assurance automatizado con IA** para call centers
bancarios. Monorepo con el backend, el frontend y la documentación.

> ⚠️ **Prototipo / demo interna** de Minsait (Grupo Indra). No usar con datos reales de clientes.

- 🌐 **En vivo:** https://callqa-ai.vercel.app · API: https://callqa-api.onrender.com
- 👤 **Acceso demo:** `admin@callqa.com` / `Admin123!`
- 🤖 **¿Eres una IA o un dev nuevo?** Lee **[`AGENTS.md`](AGENTS.md)** — la guía completa
  (arquitectura, mapa del repo, cómo correr/testear/desplegar y decisiones clave).

---

## 🚀 Arranque rápido (local)

Requisito: **Docker Desktop** abierto, y una **API key de Groq** (gratis) en `backend/.env`.

```bash
cd callqa-ai
docker compose up --build
```

- 🖥️ App: <http://localhost:3000>  ·  📚 API: <http://localhost:8000/docs>
- Detener: `Ctrl+C` o `docker compose down`.

### Activar la IA (gratis, $0)
En `backend/.env` basta una clave de **Groq** (transcripción **y** análisis):
```
GROQ_API_KEY=gsk_...
AI_PROVIDER=groq
WHISPER_PROVIDER=groq
```
> Claude/OpenAI/Azure son opcionales (de pago): cambia `AI_PROVIDER` y pon su API key.

---

## 📂 Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `backend/` | API FastAPI (+ worker Celery en local) — Python |
| `frontend/` | App web Next.js 14 (TypeScript) |
| `docs/` | Documentación de origen y sistema de diseño |
| `docker-compose.yml` | Stack local completo |
| `render.yaml` · `DEPLOY_GRATIS.md` | Despliegue gratis (Render + Vercel) |
| **`AGENTS.md`** | **Guía de desarrollo / orientación para IAs** |
| `CHANGELOG.md` · `ESTADO_DEL_PROYECTO.md` | Cambios y memoria del proyecto |

---

## 🛠️ Desarrollo y despliegue

- **Tests backend (33):** `cd backend && .venv\Scripts\python -m pytest -q` (o vía Docker).
- **Frontend en local:** `cd frontend && npm install && npm run dev`.
- **Desplegar:** `git push origin main` → Vercel y Render redepliegan solos.
- **Guía de publicación gratis:** ver **[`DEPLOY_GRATIS.md`](DEPLOY_GRATIS.md)**.

Para el detalle completo del estado y cómo trabajar, lee **[`AGENTS.md`](AGENTS.md)**.
