import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

/** Desplegable nativo con el estilo del sistema (superficie sólida, foco Rust). */
export const Select = forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => (
  <select
    ref={ref}
    className={cn(
      'h-10 w-full rounded-control border border-border bg-[var(--glass-bg)]',
      'px-3 text-body text-text-primary',
      'transition-[border-color,box-shadow] duration-ui ease-out-strong',
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
