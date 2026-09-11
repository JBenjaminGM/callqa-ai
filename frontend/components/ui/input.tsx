import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

// Estilo común de los inputs: superficie sólida, radio de control y foco Rust.
const base =
  'w-full rounded-control border border-border bg-[var(--glass-bg)] ' +
  'text-text-primary placeholder:text-text-muted ' +
  'transition-[border-color,box-shadow] duration-ui ease-out-strong ' +
  'focus:border-accent-primary focus:shadow-[0_0_0_3px_var(--glow)] ' +
  'focus:outline-none disabled:opacity-50';

/** Campo de texto con el foco resaltado en el acento de marca. */
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
