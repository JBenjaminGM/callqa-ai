# 📚 Índice de documentación — CallQA AI

> Toda la documentación del proyecto vive en esta carpeta **`docs/`**. Este es el
> punto de entrada. En la raíz del repo solo quedan `README.md` y los punteros
> `AGENTS.md` / `CLAUDE.md` (para que las IAs los descubran y apunten aquí).

**CallQA AI** — plataforma de **QA automatizado con IA** para call centers bancarios
(Minsait / Grupo Indra). Desplegada en vivo:

- 🌐 Frontend: https://callqa-ai.vercel.app · Backend: https://callqa-api.onrender.com
- 👤 Cuentas sembradas por rol: `admin@callqa.com` / `Admin123!` · `jefe@callqa.com` / `Jefe123!` · asesor (email del ejecutivo) / `Asesor123!`

> Dos repos: **`callqa-ai`** (privado, completo, fuente de verdad — este) y **`callqa`**
> (público, solo código limpio). Ver `AGENTS.md` §16.

---

## ¿Qué leo según lo que quiero hacer?

| Quiero… | Lee |
|---|---|
| **Entender y modificar el código** (dev o IA) | **`AGENTS.md`** ⭐ (empieza aquí) |
| Ver el estado actual, casos de uso, reglas de negocio y lo pendiente | `ESTADO_DEL_PROYECTO.md` |
| Ver el historial de cambios | `CHANGELOG.md` |
| **Publicar / desplegar gratis** | `DEPLOY_GRATIS.md` |
| Sistema de diseño / colores (identidad Minsait) | `DESIGN.md` |
| Presentar al cliente / stakeholders | `CallQA_AI_Presentacion.pptx` |

---

## Todos los documentos (vigentes)

- **`AGENTS.md`** — **Guía maestra de desarrollo / orientación para IAs**: estado
  actual, arquitectura, mapa del repo, cómo correr/testear/desplegar, *gotchas* y cómo
  hacer cambios. **El más importante; el punto de entrada de un chat nuevo.**
- **`ESTADO_DEL_PROYECTO.md`** — Memoria del proyecto: qué se construyó, casos de uso,
  reglas de negocio, gobernanza/compliance y qué queda.
- **`CHANGELOG.md`** — Historial de cambios (con commits).
- **`DEPLOY_GRATIS.md`** — Despliegue gratis paso a paso (Vercel + Render).
- **`DESIGN.md`** — Sistema de diseño con la **identidad oficial Minsait** (Pruno
  `#480E2A` + Gris Cerámica `#E3E2DA` dominan, Fucsia `#FF0054` de acento; ForFuture
  Sans; contenedores achaflanados). *La fuente de verdad del color es
  `frontend/app/globals.css` + `tailwind.config.ts`.*
- **`CallQA_AI_Presentacion.pptx`** — Slides para presentar al cliente.

> Los specs de origen numerados (`01`–`07`) y la guía de Railway se **consolidaron**
> en los docs canónicos de arriba y se eliminaron para mantener `docs/` mínimo y
> coherente. Toda referencia histórica a "Aetheric Intelligence", paleta Índigo/Slate,
> Railway o "vista previa/prototipo" está **obsoleta** (ver `AGENTS.md`).

---

> **Nota:** las rutas a código (`backend/...`, `frontend/...`) son relativas a la
> **raíz del repositorio**.
