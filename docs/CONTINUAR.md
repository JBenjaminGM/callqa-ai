# Continuar el trabajo

> **Lee esto primero si acabas de entrar al proyecto.** Es el traspaso entre sesiones:
> dónde estamos, qué sigue y qué te va a hacer perder tiempo si no lo sabes.
>
> Última actualización: 9 sep 2026, al terminar la Fase 1.

---

## En una frase

CallAIbrate es una plataforma de control de calidad de llamadas con IA. **El destino es
un portafolio**, no vender el producto — eso decide todas las prioridades. Estamos
ejecutando un plan de cinco fases; las dos primeras están hechas.

Antes de tocar nada, lee **[`ARQUITECTURA.md`](ARQUITECTURA.md)** (cómo funciona) y
**[`ACUERDOS.md`](ACUERDOS.md)** (qué se decidió y qué costaría cambiarlo).

## Dónde trabajar

```
C:\Users\Benja\Documents\callqa-ai\.claude\worktrees\laughing-kapitsa-5141df
```

Rama `claude/callqa-callibrate-redesign-036677`. **Es un worktree**: ejecuta todo desde
ahí, no desde la raíz del repositorio.

## Estado exacto

| | |
|---|---|
| Último commit | `8164736` — Fase 1 |
| **Sin subir a `origin/main`** | `26a6c55` (Fase 0) y `8164736` (Fase 1) |
| Tests backend | **95**, todos en verde |
| Migraciones | 0001–0008 |

**Los dos commits siguen sin push a propósito**: el usuario pidió que se le avisara antes
de subirlos. Pregúntale antes de hacer `git push`.

---

## Lo que ya está hecho

### Fase 0 · Que la demo exista (`26a6c55`)
- `backend/scripts/demo_conversations.py`: seis conversaciones en español, dos por
  ejecutivo (una que cumple el protocolo y otra que falla), con tiempos **medidos sobre
  el audio real**, no estimados.
- `backend/demo_audio/`: las seis grabaciones a calidad telefónica (8 kHz mono).
- `backend/scripts/seed_demo.py`: 67 llamadas en 90 días con tendencias intencionadas
  (María sube 64→85, Lucía baja 87→78, Carlos estable). Semilla fija, sin IA, sin coste.
- Cuenta de demostración de solo lectura (`users.is_readonly`, migración 0008). El
  guardarraíl vive en `get_current_user`, así que ningún endpoint nuevo se lo salta.
- README público con capturas (`capturas/`).

### Fase 1 · Quitar fricciones (`8164736`)
- **Pesos de la rúbrica relativos**: mueves uno y los demás se reajustan solos. Deslizador,
  candado por fila y botón de repartir por igual.
- La lista de llamadas **se refresca sola** mientras haya alguna procesándose.
- **N+1 del panel** resuelto (`selectinload` en `done_analyses`).
- **Rescate de llamadas atascadas** a los 20 minutos.
- **Acciones en lote**: selección múltiple, asignación masiva y borrado.
- Código muerto retirado (`get_rubric_weights`, `isUnassigned`, `useCallStatus`).

---

## Lo que sigue

El plan completo, con el porqué de cada cosa, está en el artefacto
<https://claude.ai/code/artifact/0736a828-5247-4c0a-911d-71bf3c405a4f>
y la auditoría que lo originó en
<https://claude.ai/code/artifact/fb1c7a81-572f-4eef-8aa2-624149103f2a>.

### Fase 2 · Calibrar — **la siguiente, y la que más importa**

Es el diferencial del proyecto. Hoy **la IA puntúa y su palabra es definitiva**: no hay
forma de revisar, corregir ni discutir una nota. En control de calidad de call centers,
«calibración» es un término técnico —varios evaluadores puntúan la misma llamada a
ciegas y se compara la diferencia— y el producto lleva ese nombre sin hacerlo.

1. **Revisión humana de una nota.** El jefe corrige las puntuaciones por dimensión,
   escribe el motivo y queda registrado quién y cuándo. **La nota de la IA no se pisa**:
   se guardan las dos para poder compararlas. Necesita migración 0009.
2. **Sesión de calibración.** El jefe puntúa a ciegas —sin ver lo que dijo la IA— y al
   terminar se revela la comparación.
3. **Panel de acuerdo IA-humano.** En qué dimensiones discrepan más. Si «Manejo de
   objeciones» discrepa un 30%, ese criterio está mal escrito y el sistema lo señala.

**Decisión ya tomada:** lo hace el rol `jefe` que ya existe. Nada de un cuarto rol de
analista de calidad: es lo estándar del sector pero en una demo no se ve, y añade
permisos, pruebas y pantallas para nada.

### Fase 3 · Cerrar el ciclo
- El asesor puede acusar recibo, comentar una evaluación y pedir revisión. Hoy su panel
  tiene **un solo botón**: ve su nota y no puede hacer nada con ella.
- El panel abre con «a quién escuchar hoy y por qué» en vez de con medias.
- Subir una carpeta entera arrastrándola.

### Fase 4 · Documentación coherente
- **`HISTORIA.md`**: absorbe `LINEA_DEL_TIEMPO.md` (se solapan) y **las entradas del
  changelog anteriores al rebrand**. Decisión del usuario: el `CHANGELOG.md` vigente
  arranca en CallAIbrate; las entradas viejas **se mueven, no se reescriben** —
  reescribirlas dejaría falsas frases como «identidad de marca Minsait en toda la app».
- `ACUERDOS.md` se queda solo con acuerdos vigentes: fuera los que son historia
  disfrazada, como el A-02 («la identidad anterior está retirada»).
- Objetivo comprobable: buscar la marca anterior en todo el repo solo debe dar
  resultados dentro de `HISTORIA.md`.

---

## Cómo verificar que todo sigue bien

```bash
cd backend && "C:/Users/Benja/Documents/callqa-ai/backend/.venv/Scripts/python.exe" -m pytest -q
```

```bash
cd frontend && npx tsc --noEmit && npm run lint && npm run build
```

```bash
docker compose up -d --build
```

App en <http://localhost:3000>, API en <http://localhost:8000/docs>.

**Cuenta de demostración:** `demo@callaibrate.com` / `CallAIbrate-Demo-2026` (solo lectura).
Las contraseñas de admin y jefe se generan al azar en cada base nueva y se imprimen una
sola vez: `docker compose logs api | grep -A 8 CREDENCIALES`.

---

## Lo que te hará perder tiempo si no lo sabes

1. **`.venv` y `node_modules` viven en el repositorio principal**, no en el worktree.
   Para los tests usa el intérprete de `C:\Users\Benja\Documents\callqa-ai\backend\.venv`.
   Para el frontend hace falta `npm ci` dentro del worktree.
2. **El stack Docker del repositorio principal ocupa el puerto 8000.** Si `docker compose
   up` no arranca, párala: `docker stop callqa-ai-api-1 callqa-ai-worker-1
   callqa-ai-postgres-1 callqa-ai-redis-1`.
3. **`npx next start` sobrevive a que se mate la tarea.** Si el navegador muestra una
   versión antigua, es que quedó un servidor huérfano en el 3000: mátalo por puerto antes
   de arrancar el nuevo build.
4. **Chrome cachea agresivamente el frontend local.** Si acabas de reconstruir y ves la
   interfaz vieja, comprueba con otro navegador antes de dar por roto el código.
5. **Las columnas de fecha son *naive*.** Nunca compares con un `datetime` con zona
   horaria: usa `datetime.now(timezone.utc).replace(tzinfo=None)`.
6. **`useAuthStore.persist` no existe durante el prerender del servidor.** Solo se puede
   leer dentro de un `useEffect`; hacerlo en el cuerpo del componente rompe `next build`.
7. **Al redesplegar se borran los audios** (`STORAGE_PROVIDER=local`). Reintentar una
   llamada ya subida falla con `No such file or directory`: hay que volver a subirla.
8. **El catálogo de modelos de Groq cambia sin avisar.** Si el análisis da `404
   model_not_found`, elige otro de <https://console.groq.com/docs/models> y cámbialo en
   `render.yaml` **y** en la variable `AI_MODEL_GROQ` del panel de Render.
9. **La PostgreSQL del plan gratuito de Render caduca a los 30 días** y se elimina con
   todo dentro. Ya pasó una vez. El workflow de copias existe pero necesita el secreto
   `DATABASE_URL` en GitHub.

## Cómo trabajar en este proyecto

- **De forma autónoma**: ejecuta git, docker, dependencias, migraciones, pruebas y builds
  sin pedir confirmación paso a paso.
- **Nada se da por bueno sin probarlo de verdad** contra el sistema real. Así aparecieron
  los tres fallos que nadie habría visto: la base de datos borrada, la sesión que se
  cerraba al recargar y el modelo de Groq retirado.
- **No introduzcas claves ni contraseñas en formularios.** Configurar, diagnosticar,
  desplegar y verificar, sí. Escribir una API key en un campo, no: eso lo hace el usuario.
- **Pregunta antes de**: hacer `push`, borrar datos o renombrar servicios.
- **Escribe en español**, igual que el resto del proyecto.
