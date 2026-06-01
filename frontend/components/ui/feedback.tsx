import { cn } from '@/lib/utils';

/** Spinner de carga circular. */
export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        'inline-block h-5 w-5 animate-spin rounded-full',
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
    <div className="rounded-lg border border-danger/30 bg-danger/10 p-4 text-body text-danger">
      {message}
    </div>
  );
}
