---
name: Aetheric Intelligence
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1b1b1d'
  surface-container: '#1f1f21'
  surface-container-high: '#2a2a2b'
  surface-container-highest: '#353436'
  on-surface: '#e4e2e4'
  on-surface-variant: '#e8bcbe'
  inverse-surface: '#e4e2e4'
  inverse-on-surface: '#303032'
  outline: '#ae8789'
  outline-variant: '#5e3e41'
  surface-tint: '#ffb2b8'
  primary: '#ffb2b8'
  on-primary: '#67001d'
  primary-container: '#ff506d'
  on-primary-container: '#5b0018'
  inverse-primary: '#be003c'
  secondary: '#ffb0cc'
  on-secondary: '#561a35'
  secondary-container: '#72304c'
  on-secondary-container: '#f29cbc'
  tertiary: '#69dbab'
  on-tertiary: '#003825'
  tertiary-container: '#27a377'
  on-tertiary-container: '#003120'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdadb'
  primary-fixed-dim: '#ffb2b8'
  on-primary-fixed: '#40000e'
  on-primary-fixed-variant: '#91002c'
  secondary-fixed: '#ffd9e4'
  secondary-fixed-dim: '#ffb0cc'
  on-secondary-fixed: '#3b0420'
  on-secondary-fixed-variant: '#72304c'
  tertiary-fixed: '#86f8c5'
  tertiary-fixed-dim: '#69dbab'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005138'
  background: '#131315'
  on-background: '#e4e2e4'
  surface-variant: '#353436'
  slate-navy: '#0b1020'
  indigo: '#6366f1'
  indigo-strong: '#4f46e5'
  canvas-light: '#f6f7fb'
  surface-white: '#ffffff'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 72px
    fontWeight: '700'
    lineHeight: 80px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.01em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter-desktop: 32px
  margin-desktop: 64px
  gutter-mobile: 16px
  margin-mobile: 20px
---

## Brand & Style
The design system embodies a "High-Tech Editorial" aesthetic, merging the precision of AI-driven analytics with the sophisticated storytelling of premium consulting. The brand personality is authoritative yet visionary, positioning the onboarding process as an immersive journey rather than a bureaucratic task.

The visual style utilizes **Glassmorphism** and **Corporate Modernism**. It relies on translucent layers, soft background blurs, and vibrant accent glows to simulate a digital environment that feels tangible and high-end. Layouts should prioritize whitespace and "breathable" content blocks, echoing the pacing of a prestige magazine.

## Colors
> **Paleta vigente (jun 2026): Índigo / Slate.** La implementación canónica son las variables CSS de `frontend/app/globals.css`; este documento es una referencia, no un dogma.

The palette is anchored by **Indigo** (#4f46e5 en claro / #6366f1 en oscuro), used for primary actions, links and data highlights — a professional, trustworthy tone well suited to a banking context. The foundation is a **Slate-navy** canvas in dark mode and a cool off-white in light mode (a calmer, more corporate alternative to the previous Electric Rose / Deep Plum).

- **Dark Mode (Default):** Deep slate-navy canvas (#0b1020). Translucency is applied to surfaces to let subtle background gradients peek through.
- **Light Mode:** Cool off-white canvas (#f6f7fb) with pure white surfaces. Slate tones provide deep-contrast text and structure.
- **AI Accents:** Soft radial gradients transitioning from Indigo (with a hint of cyan) to transparent for "glow" effects behind key interface elements.

## Typography
The system uses **Inter** exclusively to achieve a clean, geometric, and systematic feel. The hierarchy is heavily weighted toward large "Display" and "Headline" sizes to facilitate editorial storytelling. 

Tight letter-spacing is used for large headlines to maintain a premium, "locked-in" appearance. Body text should maintain generous line heights (1.5x minimum) to ensure readability during dense consulting assessments. Use `label-caps` for section headers and metadata to provide a technical contrast to the fluid display type.

## Layout & Spacing
The layout follows an **Editorial Fluid Grid**. It uses a 12-column structure on desktop with wide gutters (32px) to prevent the UI from feeling cluttered. 

- **Storytelling Sections:** Content should be centered with wide margins (64px+) to mimic the feel of a printed report.
- **Dynamic Padding:** Components like cards and modals should use consistent increments of the 8px base unit. 
- **Reflow:** On mobile, margins tighten to 20px, and typography scales aggressively. 12 columns collapse to 4, prioritizing a single-column vertical flow for onboarding forms.

## Elevation & Depth
Depth is created through **Glassmorphism** rather than traditional drop shadows. Surfaces are treated as frosted panes with varying levels of backdrop-blur (12px to 40px).

- **Surface Tiers:** Backgrounds use the primary hex; containers use a semi-transparent version (e.g., `rgba(255, 255, 255, 0.05)` in dark mode) with a 1px solid white border at 10% opacity.
- **AI Glows:** High-importance elements (like the current active step in onboarding) feature a subtle "glow" — a soft, blurred shadow using the Indigo color with high diffusion and low opacity.
- **Micro-shadows:** Only used for functional clarity on top-level modals to separate them from the glass stack.

## Shapes
The shape language is **Rounded**, balancing the tech-heavy aesthetic with human-centric softness. 

- **Primary Components:** Use 0.5rem (8px) for buttons and inputs.
- **Cards and Modals:** Use 1rem (16px) or 1.5rem (24px) for large layout containers to emphasize the "glass pane" metaphor.
- **Progress Indicators:** Use pill-shaped (full rounding) for status chips and progress bars to provide a distinct visual contrast to the structural rectangular grid.

## Components
- **Smart Buttons:** Use a solid Indigo fill (#4f46e5 / #6366f1) for primary actions. The hover state should include a subtle outer glow. Secondary buttons use the "ghost" style with a glass background and a 1px border.
- **Glass Cards:** Feature a `backdrop-filter: blur(20px)` and a thin internal stroke to catch the "light." Content within cards should follow the editorial grid.
- **Immersive Inputs:** Text fields are semi-transparent with a bottom-border only or a very subtle ghost-box. Focus states are indicated by the border color shifting to Indigo and a micro-glow.
- **Onboarding Chips:** Small, pill-shaped tags used for multi-select categories. Inactive chips are low-opacity slate/gray; active chips are Indigo with white text.
- **Interactive Lists:** Used for step-by-step consulting modules. Each list item should have a hover state that slightly increases its backdrop-blur and scale.