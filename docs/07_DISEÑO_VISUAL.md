# 🎨 Sistema de Diseño — CallQA AI

> ⚠️ **DOCUMENTO OBSOLETO.** Describe la paleta anterior (vino/borgoña con magenta). La paleta vigente es **Índigo/Slate**; la referencia actual es `docs/DESIGN.md` y la implementación canónica `frontend/app/globals.css`.

> **Paleta de colores y guías visuales para el frontend**

---

## 🎯 Concepto general

**Estilo:** Moderno corporativo con personalidad — paleta vino/borgoña con acentos magenta/rosa.
**Mood:** Premium, sofisticado, confiable (apropiado para sector bancario).
**Soporte:** Modo claro + Modo oscuro (toggle obligatorio en el header).

---

## 🌙 MODO OSCURO

### Paleta completa

| Token | Hex | Uso | Preview |
|---|---|---|---|
| `--bg-primary` | `#4B0024` | Fondo principal de la app | 🟫 Borgoña oscuro |
| `--bg-secondary` | `#65002F` | Variaciones de fondo, cards secundarios | 🟫 Vino profundo |
| `--bg-card` | `#D9D4CF` | Fondos de cards (contraste claro sobre vino) | ⬜ Gris cálido claro |
| `--accent-primary` | `#FF005C` | CTAs, botones principales, títulos resaltados | 🔴 Magenta intenso |
| `--accent-secondary` | `#E61B72` | Acentos secundarios, hover states | 🔴 Rosa fucsia |
| `--text-primary` | `#F5F1EE` | Tipografía principal sobre fondos oscuros | ⬜ Blanco cálido |
| `--text-secondary` | `#A89A9E` | Texto secundario, labels, captions | ⬜ Gris topo |
| `--shadow` | `#2A0014` | Sombras, contraste profundo, bordes | ⬛ Negro vino |

### Aplicación recomendada

```
┌────────────────────────────────────────────────┐
│  HEADER (#65002F)                              │  ← bg-secondary
│  Logo · Nav · [🌙 Toggle] · Avatar             │
├────────────────────────────────────────────────┤
│                                                 │
│  ┌──── Sidebar ────┐  ┌──── Content ────────┐ │
│  │ (#65002F)       │  │  (#4B0024)           │ │  ← bg-primary
│  │                 │  │                      │ │
│  │ • Dashboard     │  │  ┌─ Card (#D9D4CF)─┐│ │
│  │ • Llamadas      │  │  │ Texto: #2A0014  ││ │  ← card sobre vino
│  │ • Ejecutivos    │  │  │ KPI: #FF005C    ││ │
│  │                 │  │  └─────────────────┘│ │
│  │                 │  │                      │ │
│  │                 │  │  [Botón: #FF005C]   │ │  ← accent-primary
│  └─────────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────┘
```

---

## ☀️ MODO CLARO

### Paleta completa

| Token | Hex | Uso | Preview |
|---|---|---|---|
| `--bg-primary` | `#F4F0ED` | Fondo general de la app | ⬜ Crema claro |
| `--bg-card` | `#FCFAF8` | Cards, paneles, modales | ⬜ Blanco cálido |
| `--bg-accent` | `#F4C9D6` | Fondos de acento light, badges suaves | 🌸 Rosa pastel |
| `--accent-primary` | `#E84F7A` | Botones primarios, highlights, CTAs | 🌸 Rosa acento |
| `--accent-secondary` | `#F06A93` | Números destacados, métricas, cards activos | 🌸 Rosa suave |
| `--text-primary` | `#2A0A16` | Títulos principales, texto fuerte | ⬛ Vino oscuro |
| `--text-secondary` | `#4A2333` | Texto secundario fuerte, subtítulos | 🟫 Marrón ciruela |
| `--text-muted` | `#A38D93` | Texto auxiliar, captions, placeholders | ⬜ Gris rosado |
| `--border` | `#D9D0CC` | Bordes, divisiones, separadores | ⬜ Gris beige |

### Aplicación recomendada

```
┌────────────────────────────────────────────────┐
│  HEADER (#FCFAF8)                              │  ← bg-card
│  Logo · Nav · [☀️ Toggle] · Avatar             │
├────────────────────────────────────────────────┤
│                                                 │
│  ┌──── Sidebar ────┐  ┌──── Content ────────┐ │
│  │ (#FCFAF8)       │  │  (#F4F0ED)           │ │  ← bg-primary
│  │ Border #D9D0CC  │  │                      │ │
│  │                 │  │  ┌─ Card (#FCFAF8)──┐│ │
│  │ • Dashboard     │  │  │ Título: #2A0A16  ││ │
│  │ • Llamadas      │  │  │ KPI: #F06A93     ││ │  ← accent-secondary
│  │ • Ejecutivos    │  │  │ Border: #D9D0CC  ││ │
│  │                 │  │  └──────────────────┘│ │
│  │                 │  │                      │ │
│  │                 │  │  [Botón: #E84F7A]    │ │  ← accent-primary
│  └─────────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────┘
```

---

## 🎨 Colores semánticos (ambos modos)

Para estados (éxito, error, warning, info), añadimos estos colores que funcionan en ambos modos:

| Estado | Hex | Uso |
|---|---|---|
| `--success` | `#10B981` | Scores 80-100 (Excelente), confirmaciones |
| `--warning` | `#F59E0B` | Scores 60-79 (Aceptable), alertas |
| `--danger` | `#EF4444` | Scores 0-59 (Requiere atención), errores |
| `--info` | `#3B82F6` | Información general, links |

---

## 📝 Tipografía

### Fuentes recomendadas (vía Google Fonts)

```
Display (títulos grandes):  Inter, weight 700-800
Body (texto general):       Inter, weight 400-500
Mono (datos/timestamps):    JetBrains Mono o Fira Code
```

### Escala tipográfica

| Token | Tamaño | Uso |
|---|---|---|
| `text-display` | 36px / 700 | Hero, títulos de página |
| `text-h1` | 28px / 700 | Títulos de sección |
| `text-h2` | 22px / 600 | Subtítulos |
| `text-h3` | 18px / 600 | Títulos de cards |
| `text-body` | 14px / 400 | Texto general |
| `text-small` | 12px / 400 | Captions, labels |
| `text-kpi` | 48px / 800 | Números grandes en dashboard |

---

## 🎁 Componentes clave (referencia visual)

### Card de KPI (Dashboard)

```
┌──────────────────────────────┐
│  📞 Llamadas analizadas      │  ← label, text-small, text-secondary
│                              │
│    1,247                     │  ← KPI, text-kpi, accent-primary
│                              │
│  ↑ 12% vs mes anterior       │  ← delta, text-small, success
└──────────────────────────────┘
```

### Card de Llamada (Listado)

```
┌──────────────────────────────────────────────────┐
│ 👤 María González              Score: ●● 78     │
│ Tarjetas Premium · Hace 2h     ✅ Procesado     │
└──────────────────────────────────────────────────┘
   ↑ Avatar     ↑ Texto principal       ↑ Badge de score con color semántico
```

### Botón primario

```
Light mode:  [🔘 Subir llamada ]  ← bg #E84F7A, text white
Dark mode:   [🔘 Subir llamada ]  ← bg #FF005C, text #F5F1EE
Hover:                                        bg ligeramente más oscuro
Disabled:                                     opacity 50%
```

### Score visualization (radar chart)

Usar los colores semánticos para las 7 dimensiones según el score:
- 0-59 → `--danger` (rojo)
- 60-79 → `--warning` (amarillo)
- 80-100 → `--success` (verde)

El relleno del radar en el accent del modo (rosa) con opacidad 0.3.

---

## 🌗 Implementación técnica (Tailwind + CSS Variables)

### `globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Modo claro (default) */
:root {
  --bg-primary: #F4F0ED;
  --bg-card: #FCFAF8;
  --bg-accent: #F4C9D6;
  --accent-primary: #E84F7A;
  --accent-secondary: #F06A93;
  --text-primary: #2A0A16;
  --text-secondary: #4A2333;
  --text-muted: #A38D93;
  --border: #D9D0CC;

  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --info: #3B82F6;
}

/* Modo oscuro */
.dark {
  --bg-primary: #4B0024;
  --bg-secondary: #65002F;
  --bg-card: #D9D4CF;
  --accent-primary: #FF005C;
  --accent-secondary: #E61B72;
  --text-primary: #F5F1EE;
  --text-secondary: #A89A9E;
  --shadow: #2A0014;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  transition: background-color 0.2s, color 0.2s;
}
```

### `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          card: 'var(--bg-card)',
          accent: 'var(--bg-accent)',
        },
        accent: {
          primary: 'var(--accent-primary)',
          secondary: 'var(--accent-secondary)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
        border: 'var(--border)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
        info: 'var(--info)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
};

export default config;
```

---

## ✅ Checklist visual para validación

Cuando se genere el frontend, debe cumplir con:

- [ ] Toggle modo claro/oscuro funcional en el header
- [ ] Persistencia del modo en localStorage
- [ ] Transiciones suaves al cambiar de modo (200ms)
- [ ] Contraste WCAG AA mínimo en ambos modos
- [ ] Score badges con colores semánticos (verde/amarillo/rojo)
- [ ] Cards con sombras sutiles (más pronunciadas en modo oscuro)
- [ ] Hover states en todos los elementos interactivos
- [ ] Focus rings visibles para accesibilidad (color accent)
- [ ] Loading states (skeleton screens) con los colores del modo
- [ ] Empty states ilustrados (sin llamadas, sin resultados)
