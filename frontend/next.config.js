/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 'standalone' genera un servidor Node mínimo y autocontenido en
  // .next/standalone, ideal para imágenes Docker pequeñas y de arranque rápido.
  output: 'standalone',
  // El lint se ejecuta aparte con `npm run lint`; no bloquea el build.
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
