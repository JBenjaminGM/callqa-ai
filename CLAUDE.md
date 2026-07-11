# CLAUDE.md

**Para empezar a codear en un chat nuevo:** (1) lee **[`docs/AGENTS.md`](docs/AGENTS.md)**
(guía completa: estado, arquitectura, mapa del repo, correr/testear/desplegar, *gotchas*);
(2) tu **memoria de proyecto** se carga sola (índice `MEMORY.md`). Docs en **[`docs/`](docs/)**.

Estado: plataforma **funcional y desplegada**; **Fase 2** (analítica de alto impacto:
métricas de conversación, KPIs por campaña, alertas, percentil de asesor) y **rediseño
premium de indicadores** (`components/dashboard/viz.tsx`) ya implementados. Es una
plataforma **terminada** (el banner de "prototipo/vista previa" se **retiró** de la UI;
solo queda el header interno `X-Prototype-Notice`).

Esenciales:
- **IA = Groq por defecto** (`AI_PROVIDER=groq`): Whisper large v3 + Llama 3.3 70B, gratis.
  Factory portable a Claude/OpenAI/Azure. **El proveedor lo fija la env var, nunca la BD.**
- **Procesamiento:** Celery+Redis en local (`docker compose`); **inline**
  (`PROCESS_INLINE=true`, sin worker) en Render. **Despliegue vigente = Render + Vercel**
  (Railway es HISTÓRICO: cualquier mención a Railway en comentarios/ejemplos es deuda, no el estado real).
- **Roles:** `admin`/`jefe` (gestión + analítica global) y `asesor` (solo su rendimiento).
  `is_manager` / `require_manager` protegen lo de gestión.
- **Campañas con nota de producto:** entidad `Campaign` (9 campos); se inyecta en el prompt.
- **Trabajar en `C:\Users\Benja\Documents\callqa-ai`** (NO la copia de OneDrive).
- **Tests:** desde `backend/`, `.\.venv\Scripts\python.exe -m pytest -q` (78 tests). Migraciones 0001–0007.
- **Desplegar:** `git push origin main` → Vercel + Render redepliegan solos. **`GROQ_API_KEY`
  en prod vive en el dashboard de Render (`sync: false`), no en el repo.**
- **Dos repos:** privado `callqa-ai` (completo) + público `callqa` (código limpio). Publicar
  el limpio: `ops/publish-clean.ps1` (ver AGENTS §16).
- **Diseño = identidad Minsait** (Pruno + Gris Cerámica, acento Fucsia, ForFuture Sans,
  chaflanes). Color canónico: `frontend/app/globals.css` + `tailwind.config.ts`.
  (Índigo/Slate, "Aetheric Intelligence", glassmorphism/backdrop-blur están OBSOLETOS.)
