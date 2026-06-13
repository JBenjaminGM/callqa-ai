import { cn } from '@/lib/utils';

/**
 * Tarjeta "contenedor" Minsait: superficie sólida con chaflán (chamfer) en las
 * cuatro esquinas, todas iguales. Plana, sin sombra (el clip-path no recorta
 * sombras); el chaflán se lee por el contraste de relleno con el lienzo.
 */
export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'chamfer animate-fade-in bg-bg-card p-5 text-text-primary',
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
