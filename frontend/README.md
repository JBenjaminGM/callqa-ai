# 🎨 CallQA AI — Frontend

Interfaz web de la plataforma de Quality Assurance automatizado para call centers
bancarios (Minsait / Grupo Indra). Construida con **Next.js 14**, TypeScript y
Tailwind CSS.

> ⚠️ **Vista previa — entorno de evaluación.** No utilizar con datos reales de
> clientes sin la aprobación previa de Compliance.

---

## 1. ¿Qué es esto?

La aplicación que usan los distintos roles de QA. La navegación y la redirección
se adaptan al rol:

- **admin / jefe** (mismos permisos): suben y siguen llamadas, ven el dashboard
  global y los perfiles de ejecutivos, gestionan el equipo, las campañas, la
  rúbrica y los umbrales QA. Redirigen a `/dashboard`.
- **asesor:** solo ve su ficha, sus llamadas y su panel **"Mi rendimiento"**
  (`/mi-panel`); recibe los demás accesos bloqueados por guard de rol.

Se conecta al backend de CallQA AI mediante su API REST.

---

## 2. Stack tecnológico

| Componente | Tecnología |
|---|---|
| Framework | Next.js 14 (App Router) |
| Lenguaje | TypeScript |
| Estilos | Tailwind CSS + variables CSS (modo claro/oscuro) |
| Datos del servidor | TanStack Query + Axios |
| Estado de sesión | Zustand (persistido en localStorage) |
| Formularios | React Hook Form + Zod |
| Gráficos | Recharts |
| Tipografía | ForFuture Sans (woff2 locales en `public/fonts`) |
| Iconos | lucide-react |

---

## 3. Requisitos previos

- **Node.js 18 o superior** — https://nodejs.org
- El **backend de CallQA AI** corriendo (local con Docker, o desplegado en Render).

---

## 4. Configuración local (paso a paso)

```bash
# 1. Sitúate en la carpeta del proyecto
cd callqa-ai/frontend

# 2. Copia el archivo de variables de entorno
#    En Windows (PowerShell):  Copy-Item .env.local.example .env.local
cp .env.local.example .env.local

# 3. Edita .env.local con la URL de tu backend
#    NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# 4. Instala dependencias
npm install

# 5. Arranca el servidor de desarrollo
npm run dev
```

Abre **http://localhost:3000**.

### Cuentas sembradas

| Rol | Email | Contraseña |
|---|---|---|
| admin | `admin@callqa.com` | `Admin123!` |
| jefe | `jefe@callqa.com` | `Jefe123!` |
| asesor | email del ejecutivo (p. ej. `maria@banco.com`) | `Asesor123!` |

> El login ya no muestra credenciales en pantalla: úsalas desde aquí.

---

## 5. Desplegar en Vercel

El despliegue vigente es **Vercel** (frontend) + **Render** (backend), gratis ($0).
Guía completa: [`../docs/DEPLOY_GRATIS.md`](../docs/DEPLOY_GRATIS.md). En vivo:
https://callqa-ai.vercel.app (API: https://callqa-api.onrender.com).

1. Sube el repositorio a GitHub.
2. Entra a https://vercel.com/new e importa el repositorio.
3. **Root Directory:** selecciona `frontend/`. Vercel detecta que es Next.js.
4. En **Environment Variables** añade la URL de tu backend en Render:

   ```
   NEXT_PUBLIC_API_URL=https://callqa-api.onrender.com/api/v1
   ```

5. Pulsa **Deploy**. En ~2 minutos tendrás una URL pública.
6. **Importante:** en el backend (Render), añade la URL de Vercel a la
   variable `CORS_ORIGINS` para que la API acepte las peticiones del frontend.

> Cold-start del plan gratis de Render: el cliente (`lib/api.ts`) tolera el
> arranque en frío del backend (timeout 90 s, reintentos y mensaje "activando el
> servidor"). Detalles en `../docs/DEPLOY_GRATIS.md`.

---

## 6. Estructura del proyecto

```
frontend/
├── app/
│   ├── layout.tsx          # Layout raíz: fuentes (ForFuture Sans), tema, providers
│   ├── providers.tsx       # TanStack Query
│   ├── page.tsx            # Redirección inicial (por rol)
│   ├── login/page.tsx      # Inicio de sesión
│   └── (main)/             # Páginas autenticadas (sidebar + header)
│       ├── layout.tsx
│       ├── dashboard/      # KPIs del equipo (admin/jefe)
│       ├── mi-panel/       # "Mi rendimiento" (asesor)
│       ├── calls/          # Listado, subida y detalle de llamadas
│       ├── agents/         # Listado y perfil de ejecutivos
│       ├── campaigns/      # Campañas: lista, crear (PDF/IA/formulario), editar
│       └── settings/       # Rúbrica, idioma y umbrales QA
├── components/
│   ├── ui/                 # Primitivos (Button, Card, Input, Badge…)
│   ├── layout/             # Sidebar, Header, banner, toggle de tema
│   ├── dashboard/          # KpiCard
│   └── charts/             # ScoreRadar
├── lib/
│   ├── api.ts              # Cliente Axios + interceptores + resiliencia cold-start
│   ├── auth.ts             # Store de sesión (Zustand) + rol
│   ├── queries.ts          # Hooks de TanStack Query
│   └── utils.ts            # Helpers (formato, scores, clases)
├── public/
│   ├── fonts/              # ForFuture Sans (woff2)
│   └── brand/              # Logo oficial Minsait
├── types/index.ts          # Tipos que reflejan la API
└── tailwind.config.ts      # Sistema de diseño
```

---

## 7. Sistema de diseño — identidad Minsait

La paleta (modo claro y oscuro) está definida como variables CSS en
`app/globals.css` (implementación **canónica**) y mapeada a Tailwind en
`tailwind.config.ts`.

- **Paleta oficial Minsait:** Pruno (#480E2A) y Gris Cerámica (#E3E2DA)
  **dominan**; Fucsia (#FF0054) **solo** como acento.
- **Modo claro por defecto** (Gris Cerámica) + modo oscuro Pruno; el toggle del
  header persiste la elección en `localStorage`.
- **Sidebar** siempre Pruno con el logo blanco.
- **Tipografía** ForFuture Sans; titulares en minúscula con la palabra clave en
  Fucsia ("calidad con impacto"); CTA = píldora Fucsia.
- **Contenedores achaflanados** (clase `.chamfer`).
- Scores con color semántico: verde (80-100), amarillo (60-79), rojo (0-59).

> La paleta Índigo/Slate y el lenguaje "Aetheric Intelligence" están **obsoletos**.

---

## 8. Solución de problemas comunes

| Problema | Solución |
|---|---|
| Error de CORS en consola | Añade la URL del frontend a `CORS_ORIGINS` en el backend. |
| "Network Error" al iniciar sesión | Verifica que el backend esté corriendo y que `NEXT_PUBLIC_API_URL` sea correcta. En Render puede ser un cold-start: espera ~50 s al primer acceso. |
| La sesión se pierde al recargar | Revisa que el navegador permita `localStorage`. |
| Los estilos no cargan | Borra `.next/` y vuelve a ejecutar `npm run dev`. |
