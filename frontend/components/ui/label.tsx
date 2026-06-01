import { cn } from '@/lib/utils';

/** Etiqueta de formulario. */
export function Label({
  className,
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label
      className={cn(
        'mb-1.5 block text-small font-medium text-text-secondary',
        className,
      )}
      {...props}
    />
  );
}
