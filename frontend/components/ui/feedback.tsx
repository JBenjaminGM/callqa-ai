import { cn } from '@/lib/utils';

/**
 * Spinner de carga circular.
 *
 * Gira en 700 ms y no en el segundo que trae Tailwind por defecto: un spinner
 * más rápido hace que la espera parezca más corta aunque el backend tarde
 * exactamente lo mismo. La percepción de velocidad cuenta tanto como la
 * velocidad real, y aquí el backend gratuito puede tardar ~50 s en despertar.
 */
export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        'inline-block h-5 w-5 animate-spin rounded-full [animation-duration:700ms]',
        'border-2 border-current border-t-transparent',
        className,
      )}
      role="status"
      aria-label="Cargando"
    />
  );
}

/** Bloque skeleton para estados de carga. */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('skeleton h-4 w-full', className)} />;
}

/** Estado vacío ilustrado (sin datos). */
export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      {icon && <div className="text-text-muted">{icon}</div>}
      <p className="text-h3 text-text-primary">{title}</p>
      {description && (
        <p className="max-w-sm text-body text-text-secondary">{description}</p>
      )}
      {action}
    </div>
  );
}

/** Mensaje de error en pantalla. */
export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-card border border-danger/30 bg-danger/10 p-4 text-body text-danger">
      {message}
    </div>
  );
}
