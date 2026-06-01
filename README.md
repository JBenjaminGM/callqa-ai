# 🎧 CallQA AI

Plataforma de **Quality Assurance automatizado con IA** para call centers
bancarios. Monorepo con el backend, el frontend y la documentación.

> ⚠️ **Prototipo / demo interna.** No usar con datos reales de clientes.

---

## 🚀 Arranque rápido

Requisito único: **Docker Desktop** instalado y abierto.

```bash
cd callqa-ai
docker compose up --build
```

La primera vez tarda unos minutos (construye las imágenes). Cuando termine:

- 🖥️ **Aplicación:** <http://localhost:3000>
- 📚 **API / documentación:** <http://localhost:8000/docs>
- 👤 **Acceso demo:** `admin@callqa.com` / `Admin123!`

Para detener todo: `Ctrl+C`, o `docker compose down`.

---

## 📂 Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `backend/` | API FastAPI + worker Celery (Python) |
| `frontend/` | Aplicación web Next.js 14 (TypeScript) |
| `docs/` | Documentación de origen del proyecto y sistema de diseño |
| `docker-compose.yml` | Levanta el stack completo en modo producción |
| `ESTADO_DEL_PROYECTO.md` | **Memoria del proyecto**: todo lo desarrollado y lo pendiente |

---

## 🔑 Activar el análisis con IA

La navegación funciona sin claves, pero para **transcribir y analizar audios**
hay que configurar las claves de API en `backend/.env`:

```
GROQ_API_KEY=gsk_...
ANTHROPIC_API_KEY=sk-ant-...
```

Después, reinicia el stack (`docker compose up --build`).
Cómo obtener las claves: ver `docs/05_GUIA_DESPLIEGUE.md`.

---

## 🛠️ Desarrollo

- **Solo backend** (con recarga en caliente): `cd backend && docker compose up`
- **Tests del backend:** `cd backend && docker compose run --rm --no-deps api pytest`
- **Frontend en local** (requiere Node 18+): `cd frontend && npm install && npm run dev`

Para entender el estado completo del desarrollo, lee
**`ESTADO_DEL_PROYECTO.md`**.
