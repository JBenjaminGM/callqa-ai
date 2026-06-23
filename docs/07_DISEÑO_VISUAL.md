# 🎨 Sistema de Diseño — CallQA AI · Identidad Minsait

> ✅ **Identidad vigente: MINSAIT (Grupo Indra) — "calidad con impacto".**
> Dominan **Pruno** y **Gris Cerámica**; **Fucsia** es solo acento. Tipografía **ForFuture Sans**, contenedores **achaflanados**, **modo claro por defecto**.
>
> - Referencia ampliada del sistema: **`DESIGN.md`**.
> - Implementación **canónica** (fuente de verdad): **`frontend/app/globals.css`** + **`frontend/tailwind.config.ts`**.
>
> ⚠️ Quedan **OBSOLETAS** las identidades anteriores: tanto el sistema **"Aetheric Intelligence" (Índigo `#4f46e5`/`#6366f1` · Slate-navy `#0b1020`)** como la antigua paleta **vino/borgoña con acentos magenta/rosa**. Ignora cualquier mención a Índigo, Slate o Inter.

> **Paleta de colores y guías visuales para el frontend**

---

## 🎯 Concepto general

**Estilo:** Corporativo Minsait, plano y editorial — Pruno + Gris Cerámica dominan, Fucsia como acento.
**Firma:** "calidad con impacto" (Tech for impact) — titulares en minúscula con la palabra clave en Fucsia.
**Mood:** Sobrio, premium, confiable (apropiado para sector bancario).
**Soporte:** Modo claro (predeterminado, Gris Cerámica) + Modo oscuro (Pruno). Toggle en el header.

---

## 🎨 Colores de marca Minsait

| Token | Hex | Uso |
|---|---|---|
| `--pruno` | `#480e2a` | Primario: logo, fondos/textos dominantes, nav activo, KPIs, gráficos |
| `--pruno-oscuro` | `#260717` | Sobriedad / overlays / lienzo del modo oscuro |
| `--fucsia` | `#ff0054` | **ACENTO ONLY** — resalte, CTA, anillo de foco |
| `--gris-ceramica` | `#e3e2da` | Fondo claro / contenedores |
| `--blanco` | `#ffffff` | Tarjetas, texto sobre Pruno |

---

## ☀️ MODO CLARO (predeterminado · Gris Cerámica)

### Paleta completa

| Token | Hex | Uso |
|---|---|---|
| `--bg-primary` | `#e3e2da` | Lienzo cerámica (fondo de la app) |
| `--bg-secondary` | `#ffffff` | Fondos secundarios |
| `--bg-card` | `#ffffff` | Tarjetas blancas achaflanadas sobre cerámica |
| `--bg-accent` | `#d6d5cc` | Tonal cerámica para hovers (sin opacidad) |
| `--accent-primary` | `#480e2a` | Pruno: nav activo, KPIs, gráficos, enlaces |
| `--accent-secondary` | `#7e2349` | Pruno tonal: avatares / acentos secundarios |
| `--text-primary` | `#480e2a` | Cuerpo en Pruno sobre cerámica |
| `--text-secondary` | `#5e4a54` | Pruno desaturado |
| `--text-muted` | `#8a7e83` | Gris cálido tenue |
| `--border` | `#c9c7bd` | Tonal cerámica (bordes, separadores) |

### Aplicación recomendada

```
┌────────────────────────────────────────────────┐
│  HEADER (#ffffff)                              │  ← bg-card / blanco
│  Logo Minsait · Nav · [☀️ Toggle] · Avatar     │
├────────────────────────────────────────────────┤
│                                                 │
│  ┌── Sidebar (Pruno) ─┐  ┌── Content ────────┐ │
│  │ (#480e2a)          │  │  (#e3e2da)         │ │  ← bg-primary cerámica
│  │ Logo BLANCO        │  │                    │ │
│  │                    │  │ ╱─ Card (.chamfer)╲│ │
│  │ • Dashboard        │  │ │ Blanco #ffffff  ││ │
│  │ • Llamadas         │  │ │ Texto: #480e2a  ││ │
│  │ • Campañas         │  │ │ KPI: #480e2a    ││ │
│  │ • Ejecutivos       │  │ ╲────────────────╱│ │
│  │                    │  │                    │ │
│  │                    │  │ ( Subir llamada )  │ │  ← CTA píldora Fucsia
│  └────────────────────┘  └────────────────────┘ │
└────────────────────────────────────────────────┘
   ↑ Sidebar SIEMPRE Pruno con logo blanco (ambos modos)
```

---

## 🌙 MODO OSCURO (Pruno Oscuro / Pruno)

### Paleta completa

| Token | Hex | Uso |
|---|---|---|
| `--bg-primary` | `#260717` | Lienzo Pruno Oscuro |
| `--bg-secondary` | `#480e2a` | Fondos secundarios (Pruno) |
| `--bg-card` | `#3a0b22` | Card Pruno tonal sobre lienzo oscuro |
| `--bg-accent` | `#5c1536` | Tonal para hovers |
| `--accent-primary` | `#ff0054` | **Fucsia**: resalta sobre el lienzo Pruno |
| `--accent-secondary` | `#9a3460` | Acento secundario |
| `--text-primary` | `#ffffff` | Tipografía principal sobre Pruno |
| `--text-secondary` | `#d9c7d0` | Texto secundario |
| `--text-muted` | `#a98b99` | Texto auxiliar |
| `--border` | `#5c1536` | Bordes, separadores |

> En modo oscuro el acento primario pasa a **Fucsia** para destacar sobre el lienzo Pruno.

---

## 🎨 Colores de estado / dataviz (paleta secundaria oficial Minsait)

Para estados (éxito, error, warning, info) y gráficas, con variante por modo:

| Estado | Claro | Oscuro | Uso |
|---|---|---|---|
| `--success` | `#246b4e` (green-4) | `#65d16f` (green-2) | Scores altos (≥ objetivo QA), confirmaciones |
| `--warning` | `#e56813` (orange-3) | `#fc8535` (orange-2) | Scores intermedios, alertas |
| `--danger` | `#d2044a` (pink-3) | `#ef659d` (pink-2) | Scores bajos / llamadas rojas, errores |
| `--info` | `#534199` (violet-4) | `#9c85ff` (violet-2) | Información general, enlaces |

---

## 📝 Tipografía

### Fuente corporativa

```
ForFuture Sans  ← tipografía oficial Minsait (woff2 LOCALES en frontend/public/fonts)
                  pesos: 300 · 400 · 400 italic · 500 · 700 · 900
Fallback:       Arial, sans-serif
Mono (datos):   JetBrains Mono
```

**Titulares Minsait:** en **minúscula** (`text-transform: lowercase`), peso Regular (400), `line-height` 1–1.1.
La **palabra clave se resalta en Fucsia** con `.hl` (dispositivo "calidad con **impacto**").
**Eyebrow/destacado** (`.destacado`): Bold MAYÚSCULAS con `letter-spacing` amplio.

### Escala tipográfica

| Token | Tamaño / peso | Uso |
|---|---|---|
| `text-display` | 40px / 400 | Hero, títulos de página |
| `text-h1` | 28px / 400 | Títulos de sección |
| `text-h2` | 22px / 400 | Subtítulos |
| `text-h3` | 18px / 400 | Títulos de cards |
| `text-body` | 14px / 400 | Texto general (line-height 1.6) |
| `text-small` | 12px / 400 | Captions, labels |
| `text-kpi` | 48px / 900 | Números grandes en dashboard |

---

## 🔷 Formas — chaflán Minsait

El lenguaje de forma es el **chaflán** (no el redondeado).

- **Contenedores** (tarjetas, paneles, modales): clase **`.chamfer`**, `--chamfer: 14px` (9px en móvil ≤ 640px). Recorta las 8 esquinas con `clip-path: polygon(...)`, idéntico en toda la app.
- **CTA primario:** **píldora Fucsia** (radio completo).
- **Scrollbar:** esquinas rectas, sin radio.

---

## 🎁 Componentes clave (referencia visual)

### Card de KPI (Dashboard) — achaflanada

```
╱──────────────────────────────╲
│  📞 llamadas analizadas       │  ← label minúscula, text-small, text-secondary
│                               │
│    1,247                      │  ← KPI, text-kpi 48/900, accent-primary (Pruno)
│                               │
│  ↑ 12% vs mes anterior        │  ← delta, text-small, success
╲──────────────────────────────╱
   ↑ borde achaflanado .chamfer
```

### Card de Llamada (Listado)

```
╱──────────────────────────────────────────────────╲
│ 👤 María González              Score: ●● 78      │
│ Tarjetas Premium · Hace 2h     ✅ Procesado      │
╲──────────────────────────────────────────────────╱
   ↑ Avatar     ↑ Texto principal     ↑ Badge de score (color de estado)
```

### CTA primario

```
Acción principal:  ( subir llamada )   ← píldora Fucsia #ff0054, texto blanco
Resto de botones:  estilo sobrio en Pruno / borde tonal
Foco (WCAG):       anillo Fucsia (outline 3px var(--fucsia))
Disabled:          opacity 50%
```

### Score visualization (radar chart)

Usar los colores de estado para las 7 dimensiones según el score:
- Bajo → `--danger`
- Intermedio → `--warning`
- Alto (≥ objetivo QA) → `--success`

Los umbrales de score son **configurables** en `/config/settings` (`qa_target_score`, `qa_red_call_threshold`, etc.). El relleno del radar usa el acento del modo con opacidad baja.

---

## 🌗 Implementación técnica (Tailwind + CSS Variables)

> Fuente de verdad: **`frontend/app/globals.css`** + **`frontend/tailwind.config.ts`**. El fragmento siguiente es ilustrativo.

### `globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ForFuture Sans — tipografía Minsait (woff2 locales en /public/fonts) */
@font-face { font-family:'ForFuture Sans'; font-weight:400; font-display:swap;
  src:url('/fonts/ForFutureSans-Regular.woff2') format('woff2'); }
/* ... pesos 300/500/700/900 + italic ... */

/* Modo claro (predeterminado · Gris Cerámica) */
:root {
  --pruno: #480e2a;
  --pruno-oscuro: #260717;
  --fucsia: #ff0054;          /* ACENTO ONLY */
  --gris-ceramica: #e3e2da;

  --bg-primary: #e3e2da;
  --bg-card: #ffffff;
  --bg-accent: #d6d5cc;
  --accent-primary: #480e2a;
  --accent-secondary: #7e2349;
  --text-primary: #480e2a;
  --text-secondary: #5e4a54;
  --text-muted: #8a7e83;
  --border: #c9c7bd;

  --success: #246b4e; --warning: #e56813; --danger: #d2044a; --info: #534199;
  --chamfer: 14px;           /* chaflán de contenedores */
}

/* Modo oscuro (Pruno Oscuro / Pruno) */
.dark {
  --bg-primary: #260717;
  --bg-secondary: #480e2a;
  --bg-card: #3a0b22;
  --bg-accent: #5c1536;
  --accent-primary: #ff0054;  /* Fucsia resalta sobre Pruno */
  --accent-secondary: #9a3460;
  --text-primary: #ffffff;
  --text-secondary: #d9c7d0;
  --text-muted: #a98b99;
  --border: #5c1536;

  --success: #65d16f; --warning: #fc8535; --danger: #ef659d; --info: #9c85ff;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'ForFuture Sans', Arial, sans-serif;
}

/* Titulares Minsait: minúscula + palabra clave en Fucsia */
h1, h2, h3, h4 { text-transform: lowercase; line-height: 1.1; }
.hl { color: var(--fucsia); }

/* Contenedor achaflanado */
.chamfer {
  clip-path: polygon(
    var(--chamfer) 0, calc(100% - var(--chamfer)) 0, 100% var(--chamfer),
    100% calc(100% - var(--chamfer)), calc(100% - var(--chamfer)) 100%, var(--chamfer) 100%,
    0 calc(100% - var(--chamfer)), 0 var(--chamfer)
  );
}
@media (max-width: 640px) { :root { --chamfer: 9px; } }

/* Foco accesible: anillo Fucsia (WCAG) */
*:focus-visible { outline: 3px solid var(--fucsia); outline-offset: 2px; }
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
        bg: { primary: 'var(--bg-primary)', secondary: 'var(--bg-secondary)',
              card: 'var(--bg-card)', accent: 'var(--bg-accent)' },
        accent: { primary: 'var(--accent-primary)', secondary: 'var(--accent-secondary)' },
        text: { primary: 'var(--text-primary)', secondary: 'var(--text-secondary)',
                muted: 'var(--text-muted)' },
        border: 'var(--border)',
        success: 'var(--success)', warning: 'var(--warning)',
        danger: 'var(--danger)', info: 'var(--info)',
        // Colores de marca Minsait
        fucsia: 'var(--fucsia)', pruno: 'var(--pruno)',
        'pruno-oscuro': 'var(--pruno-oscuro)', ceramica: 'var(--gris-ceramica)',
      },
      fontFamily: {
        sans: ['ForFuture Sans', 'Arial', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
};

export default config;
```

---

## ✅ Checklist visual para validación

El frontend debe cumplir con:

- [ ] **Modo claro por defecto** (Gris Cerámica); toggle claro/oscuro (Pruno) en el header
- [ ] Persistencia del modo en localStorage y transiciones suaves (200ms)
- [ ] **Sidebar siempre Pruno** con el logo Minsait en blanco (ambos modos)
- [ ] **Logo oficial Minsait** (`frontend/public/brand`)
- [ ] **ForFuture Sans** cargada desde woff2 locales (`frontend/public/fonts`)
- [ ] **Titulares en minúscula** con la palabra clave en Fucsia (`.hl`)
- [ ] **Fucsia solo como acento** (CTA píldora, realce, anillo de foco) — nunca dominante
- [ ] **Contenedores achaflanados** (`.chamfer`) uniformes en toda la app
- [ ] Superficies **sólidas** (sin glassmorphism/blur); bordes tonales de 1px
- [ ] Score badges con colores de estado Minsait (success/warning/danger)
- [ ] Focus rings Fucsia visibles (WCAG AA) y contraste mínimo en ambos modos
- [ ] Loading states (`skeleton`) y aparición `animate-fade-in` (respeta `prefers-reduced-motion`)
- [ ] Empty states ilustrados (sin llamadas, sin resultados)
