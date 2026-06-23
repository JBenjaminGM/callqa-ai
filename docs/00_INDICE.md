# 📚 Índice de documentación — CallQA AI

> Toda la documentación del proyecto vive en esta carpeta **`docs/`**. Este es el
> punto de entrada. En la raíz del repo solo quedan `README.md` y los punteros
> `AGENTS.md` / `CLAUDE.md` (para que las IAs los descubran y apunten aquí).

**CallQA AI** es una **vista previa para evaluación** de **QA automatizado con IA**
para call centers bancarios (Minsait / Grupo Indra). Sigue siendo un prototipo y
está **desplegada en vivo y gratis**:

- 🌐 Frontend: https://callqa-ai.vercel.app · Backend: https://callqa-api.onrender.com
- 👤 Cuentas sembradas por rol: `admin@callqa.com` / `Admin123!` · `jefe@callqa.com` / `Jefe123!` · asesor (email del ejecutivo) / `Asesor123!`

---

## ¿Qué leo según lo que quiero hacer?

| Quiero… | Lee |
|---|---|
| **Entender y modificar el código** (dev o IA) | **`AGENTS.md`** ⭐ |
| Ver el estado actual y lo pendiente | `ESTADO_DEL_PROYECTO.md` |
| Ver el historial de cambios | `CHANGELOG.md` |
| **Publicar / desplegar gratis** | `DEPLOY_GRATIS.md` |
| Presentar al cliente / stakeholders | `06_README_EJECUTIVO.md` + `CallQA_AI_Presentacion.pptx` |
| Entender el producto y casos de uso | `01_VISION_Y_CASOS_DE_USO.md` |
| Requerimientos detallados | `02_REQUERIMIENTOS.md` |
| Arquitectura y modelo de datos | `03_ARQUITECTURA_TECNICA.md` |
| Sistema de diseño / colores (identidad Minsait) | `DESIGN.md` |

---

## Todos los documentos

### ✅ Vigentes
- **`AGENTS.md`** — **Guía maestra de desarrollo / orientación para IAs**: estado actual, arquitectura, mapa del repo, cómo correr/testear/desplegar, *gotchas* y cómo hacer cambios. **El más importante.**
- **`ESTADO_DEL_PROYECTO.md`** — Memoria del proyecto: qué se construyó y qué queda.
- **`CHANGELOG.md`** — Historial de cambios (con commits).
- **`DEPLOY_GRATIS.md`** — Despliegue gratis paso a paso (Vercel + Render).
- **`06_README_EJECUTIVO.md`** — Presentación ejecutiva (cara al cliente): vista previa para evaluación, las 3 vistas por rol, campañas con nota de producto e identidad Minsait.
- **`CallQA_AI_Presentacion.pptx`** — Slides de alto impacto para presentar.
- **`01_VISION_Y_CASOS_DE_USO.md`** — Visión, casos de uso, reglas de negocio.
- **`02_REQUERIMIENTOS.md`** — Requerimientos funcionales y no funcionales.
- **`03_ARQUITECTURA_TECNICA.md`** — Stack, modelo de datos, contratos de API. Incluye roles (admin/jefe/asesor), campañas, migraciones hasta 0005 y 61 tests.
- **`DESIGN.md`** — Sistema de diseño con la **identidad oficial Minsait** (Pruno `#480E2A` + Gris Cerámica `#E3E2DA` dominan, Fucsia `#FF0054` de acento; tipografía ForFuture Sans; contenedores achaflanados). *La implementación canónica de los colores es `frontend/app/globals.css` + `tailwind.config.ts`.*

### ⚠️ Históricos / ❌ obsoletos (no usar como referencia actual)
- ⚠️ **`04_PROMPT_BACKEND.md`** — El prompt maestro con el que se *generó* el backend. Histórico; el proyecto evolucionó (ver `AGENTS.md`).
- ⚠️ **`05_GUIA_DESPLIEGUE.md`** — Guía de despliegue antigua (Railway). Para desplegar usa **`DEPLOY_GRATIS.md`**.
- ❌ **`07_DISEÑO_VISUAL.md`** — **OBSOLETO**. La paleta y el lenguaje visual vigentes son la **identidad oficial Minsait** (Pruno + Gris Cerámica + Fucsia, ForFuture Sans, chaflán); ver `DESIGN.md`. *Cualquier mención a Índigo/Slate o "Aetheric Intelligence" en docs antiguas también está obsoleta.*

---

> **Nota:** las rutas a código (`backend/...`, `frontend/...`) que aparecen en estos
> documentos son relativas a la **raíz del repositorio**.
