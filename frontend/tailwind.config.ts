import type { Config } from 'tailwindcss';

/**
 * Configuración de Tailwind para CallQA AI.
 * Los colores se mapean a variables CSS definidas en app/globals.css,
 * lo que permite el cambio de modo claro/oscuro sin recompilar.
 */
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
        // Colores de marca Minsait (acentos / contenedores fijos)
        fucsia: 'var(--fucsia)',
        pruno: 'var(--pruno)',
        'pruno-oscuro': 'var(--pruno-oscuro)',
        ceramica: 'var(--gris-ceramica)',
      },
      fontFamily: {
        // ForFuture Sans = tipografía corporativa Minsait (woff2 locales).
        sans: ['ForFuture Sans', 'Arial', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        // Titulares Minsait: peso Regular (400), minúscula (vía globals.css).
        display: ['40px', { lineHeight: '1', fontWeight: '400' }],
        h1: ['28px', { lineHeight: '1.1', fontWeight: '400' }],
        h2: ['22px', { lineHeight: '1.1', fontWeight: '400' }],
        h3: ['18px', { lineHeight: '1.1', fontWeight: '400' }],
        body: ['14px', { lineHeight: '1.6', fontWeight: '400' }],
        small: ['12px', { lineHeight: '1.5', fontWeight: '400' }],
        kpi: ['48px', { lineHeight: '1', fontWeight: '900' }],
      },
    },
  },
  plugins: [],
};

export default config;
