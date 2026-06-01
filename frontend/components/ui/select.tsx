import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

/** Desplegable nativo con estilo translúcido del sistema Aetheric. */
export const Select = forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => (
  <select
    ref={ref}
    className={cn(
      'h-10 w-full rounded-lg border border-border bg-[var(--glass-bg)]',
      'backdrop-blur px-3 text-body text-text-primary transition-all',
      'focus:border-accent-primary focus:shadow-[0_0_0_3px_var(--glow)]',
      'focus:outline-none',
      className,
    )}
    {...props}
  >
    {children}
  </select>
));
Select.displayName = 'Select';
