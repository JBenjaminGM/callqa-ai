import { cn } from '@/lib/utils';

/**
 * Tarjeta "contenedor": superficie sólida sobre el lienzo paper, radio de 8px y
 * sombra sutil. Sin gradientes ni glassmorphism (docs/BRAND.md).
 *
 * No lleva animación de entrada. La llevaba, y con quince tarjetas por pantalla
 * el panel entero parpadeaba en cada visita. La entrada se hace una sola vez, en
 * el contenedor de la pantalla (`animate-fade-in`), que es donde cumple su
 * propósito: que los datos no sustituyan al esqueleto de carga de golpe.
 */
export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-card border border-border bg-bg-card p-5',
        'text-text-primary shadow-sm',
        className,
      )}
      {...props}
    />
  );
}

export function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('text-h3 text-text-primary', className)} {...props} />
  );
}
