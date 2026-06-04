# CLAUDE.md

**Lee [`AGENTS.md`](AGENTS.md) — es la guía completa del proyecto (estado actual,
arquitectura, mapa del repo, cómo correr/testear/desplegar y gotchas).**

Esenciales que no debes olvidar:
- **IA = Groq por defecto** (`AI_PROVIDER=groq`): Whisper large v3 (transcripción) +
  Llama 3.3 70B (análisis), gratis. Factory portable a Claude/OpenAI/Azure.
- **Procesamiento:** Celery+Redis en local (`docker compose`); **inline**
  (`PROCESS_INLINE=true`, sin worker) en el despliegue gratis de Render.
- **Trabajar en `C:\Users\Benja\Documents\callqa-ai`** (NO la copia de OneDrive).
- **Tests:** desde `backend/`, `.\.venv\Scripts\python.exe -m pytest -q` (33 tests).
- **Desplegar:** `git push origin main` → Vercel + Render redepliegan solos.
- **Colores canónicos:** `frontend/app/globals.css` (Índigo/Slate).
