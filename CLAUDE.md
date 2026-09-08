# CLAUDE.md

**Para empezar a codear en un chat nuevo:** (1) lee **[`docs/AGENTS.md`](docs/AGENTS.md)**
(guía completa: estado, arquitectura, mapa del repo, correr/testear/desplegar, *gotchas*);
(2) tu **memoria de proyecto** se carga sola (índice `MEMORY.md`). Docs en **[`docs/`](docs/)**.

El producto se llama **CallAIbrate** ("Calibra la calidad de cada llamada con IA").

Estado: plataforma **funcional y desplegada**; **Fase 2** (analítica de alto impacto:
métricas de conversación, KPIs por campaña, alertas, percentil de asesor), **rediseño
premium de indicadores** (`components/dashboard/viz.tsx`) y **rebrand a CallAIbrate**
ya implementados, más el **reproductor de audio sincronizado** y la **exportación CSV**
del reporte de equipo. Es una plataforma **terminada** (el banner de "prototipo/vista
previa" se **retiró** de la UI; solo queda el header interno `X-Prototype-Notice`).

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
- **Tests:** desde `backend/`, `.\.venv\Scripts\python.exe -m pytest -q` (87 tests). Migraciones 0001–0007.
- **Desplegar:** `git push origin main` → Vercel + Render redepliegan solos. **`GROQ_API_KEY`
  en prod vive en el dashboard de Render (`sync: false`), no en el repo.**
- **Dos repos:** privado `callqa-ai` (completo) + público `callqa` (código limpio). Publicar
  el limpio: `ops/publish-clean.ps1` (ver AGENTS §16).
- **Seed sin contraseñas fijas:** se generan al azar y se imprimen una vez
  (`docker compose logs api`); fijables con `SEED_ADMIN_PASSWORD` / `SEED_JEFE_PASSWORD` /
  `SEED_ASESOR_PASSWORD`. Cuentas: `admin@callaibrate.com`, `jefe@callaibrate.com`.
- **Diseño = identidad CallAIbrate.** Fuente de verdad de la marca: **`docs/BRAND.md`**
  (paper + ink, acentos rust y gold; Manrope / Inter / IBM Plex Mono; radios 8/6 px).
  Implementación canónica del color: `frontend/app/globals.css` + `tailwind.config.ts`.
  (Minsait —Pruno/Cerámica/Fucsia, ForFuture Sans, `.chamfer`—, Índigo/Slate,
  "Aetheric Intelligence" y glassmorphism están OBSOLETOS.)
- **Infra con el nombre viejo a propósito:** los servicios de Render (`callqa-api`,
  `callqa-db`), el usuario de Postgres, las URLs de producción y la clave
  `callqa-auth` de localStorage **no** se renombraron: hacerlo implica recrear
  servicios, invalidar el volumen `pgdata` o cerrar la sesión de todos los usuarios.
