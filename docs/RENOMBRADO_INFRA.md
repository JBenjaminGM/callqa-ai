# Renombrado de la infraestructura a CallAIbrate

> El rebrand de **código, UI y documentación** ya está hecho. Lo que sigue son los
> identificadores de **infraestructura**, que aún dicen `callqa` porque renombrarlos no
> es un cambio de texto: implica recrear servicios, migrar datos o cerrar sesiones.
>
> **Nada de esto es urgente.** Todos son nombres internos que ningún usuario ve. Si no
> quieres tocarlo, la plataforma funciona perfectamente tal cual.
>
> Los pasos los ejecutas tú (requieren tus cuentas de GitHub, Render y Vercel). Yo hago
> el paso 5, el de código, **después** de que confirmes que los anteriores están hechos.

---

## Qué sigue con el nombre viejo, y por qué

| Identificador | Dónde | Por qué no se tocó |
|---|---|---|
| `callqa-api`, `callqa-db` | `render.yaml` | Cambiar `name` en el blueprint **no renombra** el servicio: Render crea uno nuevo y deja el viejo huérfano. Y cambiar el nombre de la BD rompe el `fromDatabase` que inyecta `DATABASE_URL`. |
| Usuario/BD `callqa` | `docker-compose.yml`, `config.py` | Renombrarlos **invalida el volumen `pgdata`** local: se pierden los datos de desarrollo. |
| `callqa-ai.vercel.app`, `callqa-api.onrender.com` | README, `.env.example`, keepalive | Son las URL en vivo. Cambian solas al renombrar los proyectos, no antes. |
| `JBenjaminGM/callqa-ai`, `JBenjaminGM/callqa` | GitHub | Pediste que no renombrara repos sin confirmarlo. |
| `callqa-auth` | `frontend/lib/auth.ts` (localStorage) | Cambiar la clave **cierra la sesión de todos los usuarios** que tengan un token guardado. Ganancia cero. |

---

## Orden obligatorio

**Primero la infraestructura, después el código.** Si se cambia el código antes, el
despliegue apunta a servicios que todavía no existen y producción se cae.

---

## Paso 1 — GitHub (5 minutos, sin riesgo)

1. `github.com/JBenjaminGM/callqa-ai` → **Settings** → **General** → *Repository name* →
   `callaibrate` → **Rename**.
2. Igual con el repo público `callqa` → `callaibrate-public` (o el nombre que prefieras).
3. En local, en el repo principal **y** en cada worktree:

```bash
git remote set-url origin https://github.com/JBenjaminGM/callaibrate.git
```

GitHub mantiene redirecciones desde el nombre anterior, así que los clones y los enlaces
existentes siguen funcionando. Render y Vercel siguen el repo por id, no por nombre, así
que **no** se desconectan.

---

## Paso 2 — Render (el delicado)

Render no permite renombrar un servicio sin efectos. Tienes dos caminos.

### Opción A — no renombrar (recomendada)

Deja `callqa-api` y `callqa-db` como identificadores internos. Nadie los ve: la marca
está en la UI, en el dominio y en la documentación. **Coste: cero. Riesgo: cero.**

### Opción B — migrar de verdad

Es una migración completa, con corte de servicio:

1. **Comprueba primero si la BD sigue viva.** El plan gratuito de Render caduca las bases
   PostgreSQL a los 30 días, y durante la última auditoría el backend no respondió en 90 s.
   Si la BD ya caducó, no hay nada que migrar: crea los servicios nuevos y siembra de cero.
2. Crea la base nueva `callaibrate-db` en Render.
3. Vuelca y restaura:

```bash
pg_dump "<CONNECTION_STRING_VIEJA>" -Fc -f callqa.dump
```

```bash
pg_restore -d "<CONNECTION_STRING_NUEVA>" --no-owner callqa.dump
```

4. Crea el servicio web `callaibrate-api` apuntando al mismo repo y `rootDir: backend`.
5. Configura sus variables de entorno: `GROQ_API_KEY` (la válida, ver abajo), `CORS_ORIGINS`
   con la URL de Vercel, y deja que Render genere `JWT_SECRET`.
   ⚠️ Un `JWT_SECRET` nuevo **invalida todas las sesiones**: todos vuelven a iniciar sesión.
6. Verifica el servicio nuevo: `GET /health` responde `{"status":"healthy"}` y puedes
   iniciar sesión y subir una llamada.
7. Actualiza `NEXT_PUBLIC_API_URL` en Vercel a la URL nueva y redespliega el frontend.
8. **Solo entonces** borra el servicio y la base antiguos.

---

## Paso 3 — Vercel (5 minutos)

1. Vercel → proyecto → **Settings** → **General** → *Project Name* → `callaibrate`.
2. El dominio pasa a `callaibrate.vercel.app`; Vercel conserva el anterior como alias, así
   que los enlaces antiguos siguen abriendo.
3. **Settings** → **Environment Variables** → `NEXT_PUBLIC_API_URL` apuntando al backend
   correcto (el de siempre si elegiste la opción A).

---

## Paso 4 — Postgres local (opcional)

Renombrar el usuario/BD `callqa` en `docker-compose.yml` **invalida el volumen `pgdata`**.
Si lo haces, primero:

```bash
docker compose down -v
```

y vuelve a levantar para que se siembre de cero. En producción la cadena de conexión la
inyecta Render, así que esto no aplica allí.

---

## Paso 5 — Cierre en código (lo hago yo)

Cuando confirmes qué pasos ejecutaste, actualizo en un commit aparte:

- `CORS_ORIGINS` en `backend/.env.example`
- los comentarios de URL en `frontend/.env.local.example`
- las URL "En vivo" de `README.md` y `docs/DEPLOY_GRATIS.md`
- la URL del ping en `.github/workflows/keepalive.yml`
- `$CleanDir` y `-RemoteUrl` en `ops/publish-clean.ps1`, y las referencias de repo en
  `docs/AGENTS.md §16`
- los `name` de `render.yaml`, **solo** si elegiste la opción B

---

## Aparte: la clave de Groq en producción

Independiente de todo lo anterior, y esto sí es urgente si quieres que la IA funcione en
producción:

1. Render → servicio del backend → **Environment**.
2. `GROQ_API_KEY` → pega la clave que empieza por `gsk_mIHCoA…`, la que está en tu
   `backend/.env` local. Verificada el 2026-09-07: responde `200` contra la API de Groq.
3. **Save** → Render redespliega solo.

La clave que hay ahora en Render es la que se filtró en el commit `aeda304`. Está
**revocada** (responde `401`), así que las llamadas nuevas en producción terminan en
`ERROR`. Esa clave revocada sigue en el historial público de git; no se reescribe el
historial porque está muerta y hacerlo rompería todos los clones. **No la reutilices.**
