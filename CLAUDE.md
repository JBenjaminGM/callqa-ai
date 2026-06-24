# CLAUDE.md

**Lee [`docs/AGENTS.md`](docs/AGENTS.md)** — la guía completa del proyecto (estado
actual, arquitectura, mapa del repo, cómo correr/testear/desplegar y *gotchas*).
Toda la documentación está en **[`docs/`](docs/)** (índice: `docs/00_INDICE.md`).

Esenciales:
- **IA = Groq por defecto** (`AI_PROVIDER=groq`): Whisper large v3 (transcripción) +
  Llama 3.3 70B (análisis), gratis. Factory portable a Claude/OpenAI/Azure.
- **Procesamiento:** Celery+Redis en local (`docker compose`); **inline**
  (`PROCESS_INLINE=true`, sin worker) en el despliegue gratis de Render.
- **Roles:** `admin`/`jefe` (mismos permisos: gestión + analítica global) y
  `asesor` (solo su rendimiento). `is_manager` / `require_manager` protegen lo de gestión.
- **Campañas con nota de producto:** entidad `Campaign` (ficha de oferta de 9 campos);
  se inyecta en el prompt de análisis. Se crea por formulario, asistente IA o PDF (`pypdf`).
- **Trabajar en `C:\Users\Benja\Documents\callqa-ai`** (NO la copia de OneDrive).
- **Tests:** desde `backend/`, `.\.venv\Scripts\python.exe -m pytest -q` (78 tests).
- **Desplegar:** `git push origin main` → Vercel + Render redepliegan solos.
- **Diseño = identidad Minsait** (Pruno + Gris Cerámica, acento Fucsia, ForFuture Sans,
  chaflanes). Color canónico: `frontend/app/globals.css` + `tailwind.config.ts`.
  (Indigo/Slate y "Aetheric Intelligence" están OBSOLETOS.)
