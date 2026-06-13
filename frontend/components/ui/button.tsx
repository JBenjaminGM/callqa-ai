import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variants: Record<Variant, string> = {
  // CTA principal Minsait: píldora Fucsia con etiqueta "destacado" (bold mayúsculas).
  primary:
    'bg-[var(--fucsia)] text-[var(--pruno-oscuro)] font-bold uppercase tracking-wide ' +
    'hover:-translate-y-px disabled:opacity-50',
  // Secundaria: contorno Pruno (estilo "ghost on light"), se rellena al hover.
  secondary:
    'bg-transparent text-accent-primary border-2 border-accent-primary ' +
    'hover:bg-accent-primary hover:text-white disabled:opacity-50',
  // Terciaria discreta.
  ghost:
    'bg-transparent text-text-primary hover:bg-bg-accent disabled:opacity-50',
  // Acción destructiva.
  danger:
    'bg-danger text-white font-bold uppercase tracking-wide hover:opacity-90 disabled:opacity-50',
};

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3.5 text-small',
  md: 'h-10 px-5 text-body',
  lg: 'h-12 px-7 text-body',
};

/** Botón reutilizable con las variantes de la identidad Minsait (CTA = píldora Fucsia). */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-full font-medium',
        'transition-all duration-200 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = 'Button';
