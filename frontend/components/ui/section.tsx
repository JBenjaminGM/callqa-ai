import { cn } from '@/lib/utils';

/** Eyebrow: etiqueta superior breve en mayúsculas. */
export function Eyebrow({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        'destacado text-[11px] text-text-muted',
        className,
      )}
    >
      {children}
    </span>
  );
}

/**
 * Encabezado de sección: eyebrow + título (con una palabra clave opcional en Rust
 * vía `<span class="hl">`) + acción opcional a la derecha.
 */
export function SectionHeader({
  eyebrow,
  title,
  description,
  action,
  className,
}: {
  eyebrow?: string;
  title: React.ReactNode;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex flex-wrap items-end justify-between gap-3', className)}>
      <div>
        {eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}
        <h2 className="text-h2 text-text-primary">{title}</h2>
        {description && (
          <p className="mt-0.5 text-small text-text-secondary">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}
