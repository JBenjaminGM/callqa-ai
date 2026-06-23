---
name: Minsait — Calidad con impacto
colors:
  # --- Marca Minsait (fuente de verdad: frontend/app/globals.css) ---
  pruno: '#480e2a'
  pruno-oscuro: '#260717'
  fucsia: '#ff0054'
  gris-ceramica: '#e3e2da'
  blanco: '#ffffff'
  # --- Modo claro (Minsait light · Gris Cerámica) ---
  bg-primary: '#e3e2da'
  bg-secondary: '#ffffff'
  bg-card: '#ffffff'
  bg-accent: '#d6d5cc'
  accent-primary: '#480e2a'
  accent-secondary: '#7e2349'
  text-primary: '#480e2a'
  text-secondary: '#5e4a54'
  text-muted: '#8a7e83'
  border: '#c9c7bd'
  glow: 'rgba(255, 0, 84, 0.22)'
  shadow: 'rgba(72, 14, 42, 0.1)'
  # --- Modo oscuro (Minsait dark · Pruno Oscuro / Pruno) ---
  dark-bg-primary: '#260717'
  dark-bg-secondary: '#480e2a'
  dark-bg-card: '#3a0b22'
  dark-bg-accent: '#5c1536'
  dark-accent-primary: '#ff0054'
  dark-accent-secondary: '#9a3460'
  dark-text-primary: '#ffffff'
  dark-text-secondary: '#d9c7d0'
  dark-text-muted: '#a98b99'
  dark-border: '#5c1536'
  # --- Estado / dataviz (paleta secundaria oficial Minsait digital) ---
  success: '#246b4e'       # green-4 (claro) / #65d16f green-2 (oscuro)
  warning: '#e56813'       # orange-3 (claro) / #fc8535 orange-2 (oscuro)
  danger: '#d2044a'        # pink-3 (claro) / #ef659d pink-2 (oscuro)
  info: '#534199'          # violet-4 (claro) / #9c85ff violet-2 (oscuro)
typography:
  display:
    fontFamily: ForFuture Sans
    fontSize: 40px
    fontWeight: '400'
    lineHeight: 1
    textTransform: lowercase
  h1:
    fontFamily: ForFuture Sans
    fontSize: 28px
    fontWeight: '400'
    lineHeight: 1.1
    textTransform: lowercase
  h2:
    fontFamily: ForFuture Sans
    fontSize: 22px
    fontWeight: '400'
    lineHeight: 1.1
    textTransform: lowercase
  h3:
    fontFamily: ForFuture Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 1.1
    textTransform: lowercase
  body:
    fontFamily: ForFuture Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 1.6
  small:
    fontFamily: ForFuture Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 1.5
  kpi:
    fontFamily: ForFuture Sans
    fontSize: 48px
    fontWeight: '900'
    lineHeight: 1
  destacado:
    fontFamily: ForFuture Sans
    fontWeight: '700'
    textTransform: uppercase
    letterSpacing: 0.08em
shapes:
  chamfer: 14px          # chaflán de contenedores (.chamfer); 9px en móvil
  chamfer-mobile: 9px
  cta: 9999px            # CTA = píldora Fucsia
spacing:
  unit: 8px
  container-max: 1280px
  gutter-desktop: 32px
  margin-desktop: 64px
  gutter-mobile: 16px
  margin-mobile: 20px
---

## Marca y estilo
El sistema de diseño adopta la **identidad oficial Minsait** (Grupo Indra) bajo la firma **"calidad con impacto"** (Tech for impact). La personalidad de marca es sobria, corporativa y de alto contraste: dominan **Pruno** (#480e2a) y **Gris Cerámica** (#e3e2da), y el **Fucsia** (#ff0054) aparece **solo como acento** (resalte, CTA, foco). Es el tono adecuado para un cliente de banca.

> ⚠️ El antiguo sistema **"Aetheric Intelligence" (Índigo / Slate, glassmorphism)** queda **OBSOLETO**. Cualquier referencia a Índigo `#4f46e5`/`#6366f1`, canvas Slate-navy `#0b1020` o tipografía Inter debe ignorarse.

El estilo visual es **plano y editorial corporativo**: superficies sólidas (no glassmorphism), contenedores **achaflanados** (clase `.chamfer`) con el mismo chaflán en toda la app, y titulares en **minúscula** con la palabra clave resaltada en Fucsia (dispositivo "calidad con **impacto**"). El **modo claro es el predeterminado** (lienzo Gris Cerámica); el modo oscuro usa Pruno / Pruno Oscuro.

## Colores
> **Fuente de verdad del color: `frontend/app/globals.css` + `frontend/tailwind.config.ts`.** Este documento es una referencia; las variables CSS mandan.

La paleta se ancla en **Pruno** (#480e2a) como primario (logo, navegación activa, KPIs, gráficos, enlaces, cuerpo de texto sobre cerámica) y **Gris Cerámica** (#e3e2da) como lienzo y base de contenedores. El **Fucsia** (#ff0054) se reserva como acento: realce, CTA y anillo de foco.

- **Modo claro (predeterminado):** lienzo Gris Cerámica (#e3e2da) con tarjetas blancas achaflanadas. Texto en Pruno. Hovers tonales en cerámica (`#d6d5cc`), sin opacidad.
- **Modo oscuro:** lienzo Pruno Oscuro (#260717) y superficies Pruno tonal (#3a0b22). Aquí el acento primario pasa a **Fucsia** para resaltar sobre el lienzo Pruno.
- **Acento Fucsia:** CTAs en píldora, realces puntuales y anillo de foco accesible. `--glow: rgba(255,0,84,0.22)` (0.35 en oscuro) para foco/realce.

### Estado / dataviz (paleta secundaria oficial Minsait digital)
Para estados y gráficas se usa la paleta secundaria digital de Minsait, con variantes por modo:

| Estado | Claro | Oscuro | Uso |
|---|---|---|---|
| `--success` | `#246b4e` (green-4) | `#65d16f` (green-2) | Scores altos (≥ objetivo), confirmaciones |
| `--warning` | `#e56813` (orange-3) | `#fc8535` (orange-2) | Scores intermedios, alertas |
| `--danger`  | `#d2044a` (pink-3)  | `#ef659d` (pink-2)  | Scores bajos / llamadas rojas, errores |
| `--info`    | `#534199` (violet-4) | `#9c85ff` (violet-2) | Información general, enlaces |

## Tipografía
El sistema usa **ForFuture Sans**, la tipografía corporativa de Minsait, servida con archivos **woff2 locales** desde `frontend/public/fonts` (pesos 300/400/400 italic/500/700/900). Fallback: `Arial, sans-serif`.

Los **titulares van en minúscula** (`text-transform: lowercase`, vía `globals.css`), con peso Regular (400) y `line-height` ajustado (1–1.1), reforzando el tono editorial sobrio de Minsait. La **palabra clave del titular se resalta en Fucsia** con la clase `.hl` (dispositivo "calidad con impacto"). El eyebrow/destacado (`.destacado`) va en **Bold MAYÚSCULAS** con `letter-spacing` amplio.

| Token | Tamaño / peso | Uso |
|---|---|---|
| `text-display` | 40px / 400 | Hero, títulos de página |
| `text-h1` | 28px / 400 | Títulos de sección |
| `text-h2` | 22px / 400 | Subtítulos |
| `text-h3` | 18px / 400 | Títulos de tarjeta |
| `text-body` | 14px / 400 | Texto general (line-height 1.6) |
| `text-small` | 12px / 400 | Captions, labels |
| `text-kpi` | 48px / 900 | Números grandes en dashboard |

## Layout y espaciado
El layout mantiene una rejilla corporativa con base de **8px**. Ancho de contenido máximo 1280px, gutters de 32px y márgenes de 64px en escritorio; en móvil los márgenes se estrechan a 20px y el gutter a 16px.

- **Sidebar siempre Pruno** con el logo Minsait en blanco, en ambos modos.
- **Tarjetas blancas achaflanadas** sobre el lienzo cerámica en modo claro.
- **Padding consistente** en múltiplos de la unidad de 8px.

## Elevación y profundidad
Minsait es **plano**: la profundidad se logra con **superficies sólidas, bordes tonales de 1px y sombras sutiles** (`--shadow`), no con glassmorphism ni blur. La clase `.glass` se conserva por compatibilidad pero ahora renderiza una superficie **sólida** (fondo + borde de 1px), no una capa traslúcida con backdrop-blur. El único "glow" admitido es el anillo/realce **Fucsia** de foco (`--glow`).

## Formas
El lenguaje de forma es el **chaflán Minsait**, no el redondeado.

- **Contenedores (tarjetas, paneles, modales):** clase `.chamfer` con `--chamfer: 14px` (9px en móvil, ≤ 640px), recortando las 8 esquinas mediante `clip-path: polygon(...)`. El mismo chaflán se aplica de forma uniforme en toda la app.
- **CTA primario:** **píldora Fucsia** (radio completo, `border-radius` full).
- **Scrollbar:** discreta, esquinas rectas (sin radio).

## Componentes
- **CTA primario:** píldora con relleno **Fucsia** (#ff0054) y texto blanco; reservado para la acción principal de cada vista. El resto de botones usan estilo sobrio en Pruno / borde tonal.
- **Tarjetas achaflanadas:** superficie sólida (blanca en claro, Pruno tonal en oscuro), borde tonal de 1px y recorte `.chamfer`. Sin blur.
- **Inputs:** superficie sólida con borde tonal; el foco muestra el **anillo Fucsia** accesible (`outline: 3px solid var(--fucsia)`, WCAG). El autocompletado del navegador se fuerza a respetar la superficie/texto del tema.
- **Titulares con realce:** `h1–h4` en minúscula; la palabra clave en `.hl` (Fucsia) materializa "calidad con impacto".
- **Badges de score:** colores de estado por umbral (danger/warning/success) usando la paleta secundaria Minsait.
- **Animaciones:** aparición suave `animate-fade-in` (respeta `prefers-reduced-motion`) y `skeleton` de carga con pulso sobre el borde tonal.
