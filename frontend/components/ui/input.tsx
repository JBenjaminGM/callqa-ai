import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

// Estilo común "immersive input": semitransparente, foco con micro-glow rosa.
const base =
  'w-full rounded-lg border border-border bg-[var(--glass-bg)] backdrop-blur ' +
  'text-text-primary placeholder:text-text-muted transition-all ' +
  'focus:border-accent-primary focus:shadow-[0_0_0_3px_var(--glow)] ' +
  'focus:outline-none disabled:opacity-50';

/** Campo de texto translúcido con foco resaltado en Electric Rose. */
export const Input = forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(base, 'h-10 px-3 text-body', className)}
    {...props}
  />
));
Input.displayName = 'Input';

/** Área de texto multilínea. */
export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(base, 'px-3 py-2 text-body', className)}
    {...props}
  />
));
Textarea.displayName = 'Textarea';
