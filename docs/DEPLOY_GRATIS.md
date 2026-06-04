# 🚀 Publicar CallQA AI gratis (Vercel + Render + Groq)

Guía para dejar la plataforma **accesible desde cualquier ordenador**, **sin pagar nada**.

**Arquitectura del despliegue gratis:**

```
Navegador ─▶ Frontend (Vercel, gratis) ─▶ API (Render, gratis) ─▶ PostgreSQL (Render, gratis)
                                                  │
                                                  └─▶ Groq (transcripción + análisis, gratis)
```

> Sin worker Celery ni Redis: la API procesa cada llamada **dentro de sí misma**
> (`PROCESS_INLINE=true`), que es lo que permite caber en el plan gratis.

**Antes de empezar necesitas:** (1) el repo ya en GitHub —ya lo tienes:
`JBenjaminGM/callqa-ai`—, (2) tu **API key de Groq** (`gsk_...`, gratis en
console.groq.com), (3) una cuenta de **Render** y otra de **Vercel** (ambas se
crean gratis con tu GitHub, sin tarjeta).

---

## 1) Backend + base de datos → Render

1. Entra a **https://render.com** → **Get Started** → inicia sesión con **GitHub**.
2. Arriba: **New → Blueprint**.
3. Conecta tu repositorio **`JBenjaminGM/callqa-ai`**. Render leerá el archivo
   `render.yaml` y te mostrará que va a crear: **callqa-api** (web) y **callqa-db**
   (PostgreSQL), ambos *Free*. Pulsa **Apply**.
4. Te pedirá los valores marcados como secretos. Pon:
   - **GROQ_API_KEY** = tu clave `gsk_...`
   - **CORS_ORIGINS** = pon `*` por ahora (lo afinamos en el paso 3).
5. Espera ~5 min a que construya y despliegue. Cuando esté *Live*, copia la URL
   del servicio, será algo como **`https://callqa-api.onrender.com`**.
6. Comprueba que vive: abre **`https://callqa-api.onrender.com/health`** → debe
   responder `{"status":"healthy"}`.

---

## 2) Frontend → Vercel

1. Entra a **https://vercel.com** → **Sign Up** con **GitHub**.
2. **Add New → Project** → importa **`JBenjaminGM/callqa-ai`**.
3. ⚠️ **Root Directory:** pulsa *Edit* y selecciona **`frontend`** (¡importante,
   el frontend está en esa subcarpeta!).
4. Despliega **Environment Variables** y añade:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://callqa-api.onrender.com/api/v1`  *(tu URL de Render + `/api/v1`)*
5. Pulsa **Deploy**. En ~2 min tendrás una URL como **`https://callqa-xxx.vercel.app`**.

---

## 3) Conectarlos (CORS) y listo

1. Vuelve a **Render → callqa-api → Environment**.
2. Edita **CORS_ORIGINS** y pon tu URL exacta de Vercel, p.ej.
   `https://callqa-xxx.vercel.app` (sin barra final). Guarda → se redepliega solo.
3. Abre tu **URL de Vercel** y entra con:
   - Usuario: **`admin@callqa.com`** · Contraseña: **`Admin123!`**

🎉 ¡Ya está online y accesible desde cualquier PC, gratis!

---

## ⚠️ Cosas que debes saber (del plan gratis)

- **Se "duerme":** si nadie la usa por 15 min, la API de Render se apaga. La
  **primera carga** después tarda **~40 segundos** en despertar (luego va normal).
  Para una demo, abre la web 1 min antes para "calentarla".
- **Base de datos gratis caduca ~90 días** en Render. Cuando avise, la recreas, o
  cambias a **Neon** (neon.tech, gratis y no caduca): crea una BD, copia su
  *connection string* y ponla en Render como `DATABASE_URL`.
- **Audios efímeros:** los archivos de audio no se conservan tras reinicios (el
  disco gratis no es persistente). No afecta al análisis (transcripción y scores
  se guardan en la BD); solo significa que *reintentar* una llamada vieja podría
  no encontrar su audio.
- **Seguridad:** sigue siendo un **prototipo**. Cambia la contraseña del admin y
  no subas datos reales de clientes (el audio se procesa en Groq, EE. UU.).
- **Coste total: $0.**

---

## 🔁 Actualizaciones

Cada vez que hagas `git push` a `main`, **Render y Vercel redepliegan solos**.
No tienes que hacer nada más.
