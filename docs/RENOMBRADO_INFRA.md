# Renombrado de la infraestructura a CallAIbrate

> **Estado: hecho** (8 de septiembre de 2026). Este documento queda como registro de
> qué se renombró, qué no, y por qué.

---

## Qué pasó

Al ir a renombrar la infraestructura apareció un problema mayor: **el backend de
producción llevaba dos meses caído**. Los logs de Render lo dejaban claro:

```
psycopg2.OperationalError: could not translate host name
"dpg-d8f1ie6q1p3s73denpqg-a" to address: Name or service not known
```

La base PostgreSQL del plan gratuito **caducó y Render la eliminó**. El plan gratuito
las borra a los 30 días; el último despliegue fue el 11 de julio. El servicio web seguía
"activo", pero moría al arrancar: `alembic upgrade head` no podía conectar, así que
uvicorn nunca llegaba a levantarse y `/health` no respondía nunca.

**Los datos de producción se perdieron** —llamadas, transcripciones, análisis y
usuarios— y no había copia de seguridad. No se perdieron al renombrar: ya no existían.

Eso cambió el cálculo. El motivo para *no* renombrar los servicios de Render era el
coste de migrar la base de datos. Sin datos que migrar, ese coste desapareció, así que
se aprovechó para dejar la infraestructura coherente con el nombre nuevo.

---

## Qué se renombró

| Antes | Ahora | Dónde |
|---|---|---|
| `callqa-api` | `callaibrate-api` | Servicio web de Render (`render.yaml`) |
| `callqa-db` | `callaibrate-db` | Base PostgreSQL de Render (`render.yaml`) |
| usuario/BD `callqa` | `callaibrate` | Dentro de la base de Render |
| `callqa-api.onrender.com` | `callaibrate-api.onrender.com` | URL del backend |
| `callqa-ai.vercel.app` | `callaibrate.vercel.app` | URL del frontend |

---

## Qué conserva el nombre anterior, y por qué

| Identificador | Dónde | Por qué |
|---|---|---|
| Usuario/BD `callqa` | `docker-compose.yml`, default de `config.py` | Es solo la base de **desarrollo local**. Renombrarla invalida el volumen `pgdata` y borra los datos locales. Si algún día quieres alinearla: `docker compose down -v`, cambia el nombre y vuelve a levantar. |
| `callqa-auth` | `frontend/lib/auth.ts` (localStorage) | Cambiar la clave **cierra la sesión de todos los usuarios** que tengan un token guardado. Ganancia cero. |
| Entradas de `CHANGELOG.md` | `docs/` | Son historia: describen cómo se llamaban las cosas entonces. |

---

## Lecciones para la próxima

- **El plan gratuito de Render caduca las bases PostgreSQL a los 30 días.** Si esto va a
  ser algo más que una demo, hay que pasar a un plan de pago o exportar periódicamente.
- **No había backup.** Antes de volver a meter datos que importen, hace falta un volcado
  programado (`pg_dump`) fuera de Render.
- **El almacenamiento de audios sigue siendo efímero** (`STORAGE_PROVIDER=local` sobre el
  disco del contenedor): se pierde en cada redespliegue. **Comprobado en vivo:** al
  cambiar una variable de entorno, el redespliegue vació `/data/audios/` y reintentar
  una llamada ya subida falló con `No such file or directory`. Para uso real hay que
  pasar a S3; está anotado en [`COMPLIANCE_CHECKLIST.md`](COMPLIANCE_CHECKLIST.md).
- **El catálogo de modelos de Groq cambia sin aviso.** `llama-3.3-70b-versatile` dejó de
  estar disponible para esta cuenta (`404 model_not_found`) aunque la documentación de
  Groq seguía listándolo como modelo de producción. El vigente es `openai/gpt-oss-120b`.
  Si el análisis vuelve a fallar con 404, elegir otro de
  https://console.groq.com/docs/models y cambiarlo en `render.yaml` **y** en la variable
  `AI_MODEL_GROQ` del panel de Render.
- El servicio parecía **"Active"** en el panel de Render aunque llevaba semanas sin
  servir una sola petición. El estado del panel no es un health check: el `keepalive` de
  GitHub Actions hacía ping con `|| true`, así que tampoco avisaba de nada. **Ya
  corregido:** ahora reintenta 3 veces y falla con diagnóstico.

---

## La clave de Groq

Independiente de todo lo anterior: la `GROQ_API_KEY` de Render es `sync: false`, vive
solo en el panel y **nunca en el repositorio**. La que se filtró en el commit `aeda304`
está **revocada** (responde `401`) y sigue en el historial público de git; no se
reescribe el historial porque la clave está muerta y hacerlo rompería todos los clones.
**No la reutilices.** La válida está en tu `backend/.env` local y empieza por `gsk_mIHCoA`.
