# 📘 Guía de Despliegue Paso a Paso (para no-devs)

> 📌 **Documento de referencia.** El proyecto ya está en GitHub (`JBenjaminGM/callqa-ai`) y corre en local con Docker (`docker compose up`). Con Groq por defecto el coste de IA es $0. Las secciones de Railway/Vercel/Anthropic siguen siendo válidas como referencia si quieres desplegar en la nube o cambiar de proveedor.

> **Esta guía está escrita asumiendo que NO sabes desarrollo.** Cada paso explica exactamente qué hacer y qué deberías ver.

---

## 🎯 ¿Qué vamos a hacer?

Vamos a poner tu plataforma CallQA AI **en internet** para que tu jefe pueda abrirla desde cualquier navegador. El proceso tiene 5 fases:

1. ✅ Crear cuentas en los servicios necesarios
2. ✅ Subir el código a GitHub
3. ✅ Desplegar el backend en Railway
4. ✅ Desplegar el frontend en Vercel
5. ✅ Configurar todo para que se comuniquen

**Tiempo total estimado:** 1-2 horas la primera vez.

---

## 📋 Fase 0: Preparación (antes de empezar)

### Cuentas que necesitas crear

| Servicio | Para qué | Link | Costo |
|---|---|---|---|
| **GitHub** | Guardar el código | https://github.com/signup | Gratis |
| **Railway** | Hostear el backend | https://railway.app | $5 crédito gratis, después ~$5-10/mes |
| **Vercel** | Hostear el frontend | https://vercel.com/signup | Gratis para siempre |
| **Groq** | API de transcripción | https://console.groq.com | Gratis con límites generosos |
| **Anthropic** | API de Claude (análisis IA) | https://console.anthropic.com | Pay-per-use, muy barato (~$0.02 por llamada) |

### Software a instalar en tu computadora

1. **Git** (para subir código a GitHub):
   - Mac: ya viene instalado, verifica con `git --version` en Terminal
   - Windows: descarga de https://git-scm.com/download/win
   - Linux: `sudo apt install git`

2. **Editor de código** (recomendado: VS Code):
   - https://code.visualstudio.com/

3. **Docker Desktop** (solo si quieres probar antes de desplegar):
   - https://www.docker.com/products/docker-desktop/

---

## 🔑 Fase 1: Obtener las API Keys

### 1.1 Groq API Key (Transcripción)

1. Ve a https://console.groq.com/
2. Inicia sesión con Google o crea cuenta
3. En el menú lateral, click en **"API Keys"**
4. Click en **"Create API Key"**
5. Dale un nombre (ej: "CallQA Production")
6. **COPIA LA KEY EN UN BLOC DE NOTAS** (no se mostrará de nuevo)
7. Empieza con `gsk_...`

### 1.2 Anthropic API Key (Análisis IA)

> 💡 **Opcional.** Con Groq por defecto (`AI_PROVIDER=groq`, Llama 3.3 70B, gratis) NO hace falta Anthropic y el coste de IA es **$0**. Sigue estos pasos solo si quieres usar Claude como proveedor de análisis.

1. Ve a https://console.anthropic.com/
2. Crea una cuenta
3. **IMPORTANTE:** Necesitarás añadir un método de pago, pero solo te cobran por uso real (~$0.02 por llamada)
4. Ve a **"API Keys"** en el menú
5. Click en **"Create Key"**
6. Cópiala. Empieza con `sk-ant-...`
7. Recomendación: añade $5-10 USD de crédito inicial — te durarán cientos de llamadas

### 1.3 OpenAI API Key (Opcional, alternativa)

Solo si quieres tener la opción de cambiar entre Claude y GPT.
1. Ve a https://platform.openai.com/api-keys
2. Crea cuenta y añade método de pago
3. Crea una API Key, cópiala. Empieza con `sk-...`

---

## 📦 Fase 2: Subir el código a GitHub

### 2.1 Generar el código con Claude Code

1. Crea una carpeta en tu computadora llamada `callqa-backend`
2. Abre Claude Code en esa carpeta
3. Copia el prompt completo del archivo `04_PROMPT_BACKEND.md` (la sección entre "INICIO DEL PROMPT" y "FIN DEL PROMPT")
4. Pégalo en Claude Code y deja que genere todo (~15-30 min)
5. Cuando termine, abre la carpeta con VS Code para verificar que se crearon todos los archivos

**Antes de subir a GitHub:** abre el archivo `.env.example`, copia su contenido a un nuevo archivo llamado `.env` (sin extensión `.example`) y rellena con tus API keys:

```bash
DATABASE_URL=postgresql://callqa:callqa@postgres:5432/callqa
REDIS_URL=redis://redis:6379/0
GROQ_API_KEY=gsk_tu_key_aqui
ANTHROPIC_API_KEY=sk-ant-tu_key_aqui
JWT_SECRET=cambia-esto-por-algo-aleatorio-largo
CORS_ORIGINS=http://localhost:3000
```

> ⚠️ **MUY IMPORTANTE:** El archivo `.env` **NUNCA se sube a GitHub**. El `.gitignore` que generó Claude Code ya lo excluye, pero verifica antes.

### 2.2 Probar localmente (opcional pero recomendado)

Antes de subir nada, abre una terminal en la carpeta del proyecto y ejecuta:

```bash
docker-compose up
```

Espera ~2 minutos. Cuando veas algo como `Application startup complete`, abre tu navegador en:
- http://localhost:8000/docs

Deberías ver la documentación interactiva de la API. Si llega hasta aquí, **el backend funciona**. Detén el contenedor con `Ctrl+C`.

### 2.3 Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repo: `callqa-backend`
3. Marca como **Privado** (recomendado, contiene lógica de negocio)
4. **NO** marques "Initialize with README" (porque ya tienes uno)
5. Click en **"Create repository"**
6. GitHub te mostrará comandos. Copia los de la sección **"push an existing repository"**

### 2.4 Subir el código (3 comandos)

Abre una terminal en la carpeta del proyecto y ejecuta uno por uno:

```bash
git init
git add .
git commit -m "Primera versión del backend CallQA"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/callqa-backend.git
git push -u origin main
```

Cuando te pida usuario y contraseña, GitHub ya no acepta contraseña — usa un **Personal Access Token**:
1. https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Marca `repo` como scope
4. Genera, copia el token
5. Úsalo como contraseña cuando `git push` te lo pida

✅ **Listo, tu código está en GitHub.**

---

## 🚂 Fase 3: Desplegar el Backend en Railway

### 3.1 Crear el proyecto

1. Entra a https://railway.app/
2. Inicia sesión con GitHub
3. Click en **"New Project"**
4. Selecciona **"Deploy from GitHub repo"**
5. Autoriza a Railway a acceder a tus repos
6. Selecciona `callqa-backend`
7. Railway empezará a hacer el build automáticamente

### 3.2 Añadir PostgreSQL

1. Dentro de tu proyecto, click en **"+ New"** (arriba a la derecha)
2. Selecciona **"Database" → "Add PostgreSQL"**
3. Espera unos segundos a que se aprovisione

### 3.3 Añadir Redis

1. Click en **"+ New"** otra vez
2. Selecciona **"Database" → "Add Redis"**

### 3.4 Configurar las variables de entorno del backend

1. Click en el servicio del backend (el que se llama `callqa-backend`)
2. Ve a la pestaña **"Variables"**
3. Añade estas variables una por una:

```
GROQ_API_KEY=gsk_tu_key
ANTHROPIC_API_KEY=sk-ant-tu_key
OPENAI_API_KEY=sk-tu_key  (opcional)
AI_PROVIDER=groq
WHISPER_PROVIDER=groq
JWT_SECRET=genera-uno-aleatorio-largo-aqui
JWT_EXPIRE_HOURS=8
APP_ENV=production
APP_DEFAULT_LANGUAGE=es
APP_MAX_AUDIO_SIZE_MB=100
STORAGE_PROVIDER=local
STORAGE_PATH=/data/audios
CORS_ORIGINS=https://callqa-frontend.vercel.app
```

Para `DATABASE_URL` y `REDIS_URL`, usa las **variables de referencia** de Railway:

- `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
- `REDIS_URL` = `${{Redis.REDIS_URL}}`

(Railway tiene un botón "Add Reference" que te permite hacer esto fácilmente)

### 3.5 Añadir un Volume para los audios

1. En el servicio del backend, ve a **"Settings"**
2. Scroll a **"Volumes"** → click "Add Volume"
3. Mount path: `/data`
4. Tamaño: 1 GB es suficiente para MVP

### 3.6 Crear el servicio del Worker (Celery)

1. Click en **"+ New" → "Empty Service"**
2. Nómbralo `callqa-worker`
3. Ve a **"Settings"**:
   - **Source repo:** mismo que el backend
   - **Start Command:** `celery -A app.tasks.celery_app worker --loglevel=info`
4. Copia las mismas variables de entorno del backend a este servicio
5. Asegúrate de montar el mismo volumen `/data`

### 3.7 Generar el dominio público

1. En el servicio backend principal, ve a **"Settings" → "Networking"**
2. Click en **"Generate Domain"**
3. Tendrás algo como `callqa-backend-production.up.railway.app`
4. **Anota esta URL**, la necesitarás para el frontend

### 3.8 Verificar que funciona

Abre en tu navegador:
```
https://callqa-backend-production.up.railway.app/docs
```

Deberías ver la documentación de la API. Si ves errores, revisa los logs en Railway (pestaña "Deployments").

### 3.9 Crear el usuario admin inicial

1. En Railway, abre el servicio backend
2. Ve a la pestaña **"Settings"** → **"Custom Start Command"** temporalmente
3. O usa la "Shell" de Railway si está disponible
4. Ejecuta: `python scripts/seed_data.py`

Esto crea:
- Usuario admin: `admin@callqa.com` / `Admin123!`
- 3 ejecutivos de ejemplo
- Configuración inicial de la rúbrica

---

## 🌐 Fase 4: Desplegar el Frontend en Vercel

**Nota:** Aún no hemos generado el frontend en este paso — eso es la Fase 6 del plan global. Pero cuando lo generes con Claude Code, el deploy a Vercel es así:

### 4.1 Pasos cuando tengas el frontend listo

1. Sube el código del frontend a un nuevo repo de GitHub llamado `callqa-frontend` (mismos comandos `git init`, `git add`, etc.)
2. Ve a https://vercel.com/new
3. Importa el repo `callqa-frontend`
4. Vercel detecta automáticamente que es Next.js
5. En **Environment Variables**, añade:
   ```
   NEXT_PUBLIC_API_URL=https://callqa-backend-production.up.railway.app/api/v1
   ```
6. Click **"Deploy"**
7. En ~2 minutos tendrás una URL pública tipo `callqa-frontend.vercel.app`

### 4.2 Actualizar CORS en el backend

Una vez tengas la URL de Vercel:

1. Vuelve a Railway → servicio backend → Variables
2. Edita `CORS_ORIGINS` para que sea la URL de Vercel:
   ```
   CORS_ORIGINS=https://callqa-frontend.vercel.app
   ```
3. Railway re-desplegará automáticamente

---

## ✅ Fase 5: Verificación final

Antes de mostrar a tu jefe, verifica que todo funciona:

### Checklist de demo

- [ ] La URL de Vercel abre correctamente
- [ ] Puedo hacer login con admin@callqa.com / Admin123!
- [ ] El dashboard carga sin errores
- [ ] Puedo ver los 3 ejecutivos de ejemplo
- [ ] Puedo crear un ejecutivo nuevo
- [ ] Puedo subir un audio de prueba (graba algo corto con tu celular)
- [ ] El audio pasa por los estados QUEUED → TRANSCRIBING → ANALYZING → DONE
- [ ] El análisis muestra scores en las 7 dimensiones
- [ ] El reporte PDF se descarga correctamente

### Audios de prueba recomendados

Graba 3-4 audios cortos (30-60 segundos) simulando llamadas:

1. **Llamada buena:** Saludo formal, ofrecimiento claro de productos, despedida cordial
2. **Llamada mala:** Sin saludo, tono cortante, sin mencionar promociones
3. **Llamada media:** Buen saludo pero olvida disclaimers

Esto le mostrará a tu jefe el rango de evaluación de la IA.

---

## 🆘 Solución de problemas comunes

### "Application failed to respond" en Railway

- Revisa los logs en la pestaña "Deployments"
- Verifica que `DATABASE_URL` esté como referencia, no hardcoded
- Verifica que el puerto sea `$PORT` (variable de Railway), no 8000 hardcoded

### Error CORS en el frontend

- Verifica que `CORS_ORIGINS` en Railway incluya exactamente la URL de Vercel
- Sin barra final: `https://callqa-frontend.vercel.app` (NO `https://...vercel.app/`)
- Re-despliega después de cambiar

### El audio queda en "TRANSCRIBING" para siempre

- Verifica que el servicio `callqa-worker` esté corriendo
- Revisa logs del worker — probablemente falta `GROQ_API_KEY` o está mal
- Verifica que Redis esté conectado (REDIS_URL como referencia)

### "Invalid API key" de Anthropic

- Verifica que la key empieza con `sk-ant-`
- Verifica que tu cuenta tenga saldo
- Verifica el modelo: debe ser `claude-sonnet-4-6` o similar disponible

### Costos están subiendo en Railway

- Railway cobra por uso de CPU/RAM
- Si no es horario de demo, **puedes pausar el proyecto** desde Settings
- Configura un **límite de gasto mensual** en Settings → Usage

---

## 💰 Costos esperados para tu demo

| Servicio | Costo estimado/mes |
|---|---|
| Railway (backend + worker + DB + Redis) | $8-15 |
| Vercel (frontend) | $0 |
| Groq (transcripción) | $0-2 |
| Anthropic Claude | $1-5 (depende de cuántas llamadas analices) |
| **TOTAL** | **~$10-20/mes** |

Para una demo única a tu jefe, puedes desplegarlo, hacer la demo, y luego pausar todo. Te costaría menos de $5.

---

## 📞 Soporte

Si te atascas en algún paso:

1. **Pregúntale a Claude Code** — describe exactamente el paso y el error
2. **Logs de Railway** — son tu mejor amigo cuando algo falla
3. **Verifica las variables de entorno** — el 80% de los problemas son por una variable mal configurada
4. **No mezcles claves** — la key de Groq solo va en GROQ_API_KEY, etc.
