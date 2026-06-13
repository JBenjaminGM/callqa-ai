import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'CallQA AI · Minsait',
  description:
    'Quality Assurance automatizado con IA para call centers. Minsait — tech for impact.',
};

// Script que aplica el modo claro/oscuro antes del render para evitar parpadeo.
// Por defecto = modo CLARO Minsait (Gris Cerámica); oscuro solo si se elige.
const themeScript = `
(function () {
  try {
    if (localStorage.getItem('callqa-theme') === 'dark') {
      document.documentElement.classList.add('dark');
    }
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
