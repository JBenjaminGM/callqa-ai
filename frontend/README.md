# 🎨 CallQA AI — Frontend

Interfaz web del **prototipo** de Quality Assurance automatizado para call
centers bancarios. Construida con **Next.js 14**, TypeScript y Tailwind CSS.

> ⚠️ **PROTOTIPO — DEMO INTERNA.** No utilizar con datos reales de clientes.

---

## 1. ¿Qué es esto?

La aplicación que usa el supervisor de QA para:

- Iniciar sesión.
- Subir grabaciones de llamadas y seguir su procesamiento.
- Consultar el análisis con IA (scores, recomendaciones, transcripción).
- Ver el dashboard del equipo y el perfil de cada ejecutivo.
- Gestionar el equipo de ejecutivos y la rúbrica de evaluación.

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
| Iconos | lucide-react |

---

## 3. Requisitos previos

- **Node.js 18 o superior** — https://nodejs.org
- El **backend de CallQA AI** corriendo (local o en Railway).

---

## 4. Configuración local (paso a paso)

```bash
# 1. Sitúate en la carpeta del proyecto
cd callqa-frontend

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

### Credenciales de demo

- Usuario: `admin@callqa.com`
- Contraseña: `Admin123!`

---

## 5. Desplegar en Vercel

1. Sube este repositorio a GitHub (`callqa-frontend`).
2. Entra a https://vercel.com/new e importa el repositorio.
3. Vercel detecta automáticamente que es un proyecto Next.js.
4. En **Environment Variables** añade:

   ```
   NEXT_PUBLIC_API_URL=https://tu-backend.up.railway.app/api/v1
   ```

5. Pulsa **Deploy**. En ~2 minutos tendrás una URL pública.
6. **Importante:** en el backend (Railway), añade la URL de Vercel a la
   variable `CORS_ORIGINS` para que la API acepte las peticiones del frontend.

---

## 6. Estructura del proyecto

```
callqa-frontend/
├── app/
│   ├── layout.tsx          # Layout raíz: fuentes, tema, providers
│   ├── providers.tsx       # TanStack Query
│   ├── page.tsx            # Redirección inicial
│   ├── login/page.tsx      # Inicio de sesión
│   └── (main)/             # Páginas autenticadas (sidebar + header)
│       ├── layout.tsx
│       ├── dashboard/      # KPIs del equipo
│       ├── calls/          # Listado, subida y detalle de llamadas
│       ├── agents/         # Listado y perfil de ejecutivos
│       └── settings/       # Rúbrica e idioma
├── components/
│   ├── ui/                 # Primitivos (Button, Card, Input, Badge…)
│   ├── layout/             # Sidebar, Header, banner, toggle de tema
│   ├── dashboard/          # KpiCard
│   └── charts/             # ScoreRadar
├── lib/
│   ├── api.ts              # Cliente Axios + interceptores
│   ├── auth.ts             # Store de sesión (Zustand)
│   ├── queries.ts          # Hooks de TanStack Query
│   └── utils.ts            # Helpers (formato, scores, clases)
├── types/index.ts          # Tipos que reflejan la API
└── tailwind.config.ts      # Sistema de diseño
```

---

## 7. Sistema de diseño

La paleta de colores (modo claro y oscuro) está definida como variables CSS
en `app/globals.css` y mapeada a Tailwind en `tailwind.config.ts`, siguiendo el
documento de diseño visual del proyecto:

- **Modo claro:** crema y rosa acento.
- **Modo oscuro:** Slate-navy (#0b1020) con acento Índigo (#6366f1).
- El toggle del header persiste la elección en `localStorage`.
- Scores con color semántico: verde (80-100), amarillo (60-79), rojo (0-59).

---

## 8. Solución de problemas comunes

| Problema | Solución |
|---|---|
| Error de CORS en consola | Añade la URL del frontend a `CORS_ORIGINS` en el backend. |
| "Network Error" al iniciar sesión | Verifica que el backend esté corriendo y que `NEXT_PUBLIC_API_URL` sea correcta. |
| La sesión se pierde al recargar | Revisa que el navegador permita `localStorage`. |
| Los estilos no cargan | Borra `.next/` y vuelve a ejecutar `npm run dev`. |
