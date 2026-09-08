import { cn } from '@/lib/utils';

/**
 * Tarjeta "contenedor": superficie sólida sobre el lienzo paper, radio de 8px y
 * sombra sutil. Sin gradientes ni glassmorphism (docs/BRAND.md).
 */
export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-card animate-fade-in border border-border bg-bg-card p-5',
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
