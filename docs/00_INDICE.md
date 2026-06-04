# 📚 Índice de documentación — CallQA AI

> Toda la documentación del proyecto vive en esta carpeta **`docs/`**. Este es el
> punto de entrada. En la raíz del repo solo quedan `README.md` y los punteros
> `AGENTS.md` / `CLAUDE.md` (para que las IAs los descubran y apunten aquí).

**CallQA AI** es un prototipo de **QA automatizado con IA** para call centers
bancarios (Minsait / Grupo Indra). Está **desplegado en vivo y gratis**:

- 🌐 Frontend: https://callqa-ai.vercel.app · Backend: https://callqa-api.onrender.com
- 👤 Login demo: `admin@callqa.com` / `Admin123!`

---

## ¿Qué leo según lo que quiero hacer?

| Quiero… | Lee |
|---|---|
| **Entender y modificar el código** (dev o IA) | **`AGENTS.md`** ⭐ |
| Ver el estado actual y lo pendiente | `ESTADO_DEL_PROYECTO.md` |
| Ver el historial de cambios | `CHANGELOG.md` |
| **Publicar / desplegar gratis** | `DEPLOY_GRATIS.md` |
| Presentar al jefe / stakeholders | `06_README_EJECUTIVO.md` + `CallQA_AI_Presentacion.pptx` |
| Entender el producto y casos de uso | `01_VISION_Y_CASOS_DE_USO.md` |
| Requerimientos detallados | `02_REQUERIMIENTOS.md` |
| Arquitectura y modelo de datos | `03_ARQUITECTURA_TECNICA.md` |
| Sistema de diseño / colores | `DESIGN.md` |

---

## Todos los documentos

### ✅ Vigentes
- **`AGENTS.md`** — **Guía maestra de desarrollo / orientación para IAs**: estado actual, arquitectura, mapa del repo, cómo correr/testear/desplegar, *gotchas* y cómo hacer cambios. **El más importante.**
- **`ESTADO_DEL_PROYECTO.md`** — Memoria del proyecto: qué se construyó y qué queda.
- **`CHANGELOG.md`** — Historial de cambios (con commits).
- **`DEPLOY_GRATIS.md`** — Despliegue gratis paso a paso (Vercel + Render).
- **`06_README_EJECUTIVO.md`** — Presentación ejecutiva.
- **`CallQA_AI_Presentacion.pptx`** — Slides de alto impacto para presentar.
- **`01_VISION_Y_CASOS_DE_USO.md`** — Visión, casos de uso, reglas de negocio.
- **`02_REQUERIMIENTOS.md`** — Requerimientos funcionales y no funcionales.
- **`03_ARQUITECTURA_TECNICA.md`** — Stack, modelo de datos, contratos de API.
- **`DESIGN.md`** — Sistema de diseño (paleta **Índigo/Slate**). *La implementación canónica de los colores es `frontend/app/globals.css`.*

### ⚠️ Históricos / ❌ obsoletos (no usar como referencia actual)
- ⚠️ **`04_PROMPT_BACKEND.md`** — El prompt maestro con el que se *generó* el backend. Histórico; el proyecto evolucionó (ver `AGENTS.md`).
- ⚠️ **`05_GUIA_DESPLIEGUE.md`** — Guía de despliegue antigua (Railway). Para desplegar usa **`DEPLOY_GRATIS.md`**.
- ❌ **`07_DISEÑO_VISUAL.md`** — **OBSOLETO** (describe una paleta antigua vino/borgoña). La paleta vigente es Índigo/Slate (ver `DESIGN.md`).

---

> **Nota:** las rutas a código (`backend/...`, `frontend/...`) que aparecen en estos
> documentos son relativas a la **raíz del repositorio**.
