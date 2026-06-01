import { cn } from '@/lib/utils';

/**
 * Tarjeta "panel de cristal" (glassmorphism): superficie translúcida con
 * desenfoque de fondo y un borde fino que capta la luz.
 */
export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'glass rounded-2xl p-5',
        'shadow-[0_8px_32px_-12px_var(--shadow)] animate-fade-in',
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
