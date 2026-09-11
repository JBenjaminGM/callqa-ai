import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

const variants: Record<Variant, string> = {
  // CTA principal: sólido en el acento de marca.
  primary: 'bg-rust text-white hover:opacity-90 disabled:opacity-50',
  // Secundaria: contorno, se rellena al pasar el ratón.
  secondary:
    'bg-transparent text-rust border border-rust ' +
    'hover:bg-rust hover:text-white disabled:opacity-50',
  // Terciaria discreta.
  ghost: 'bg-transparent text-text-primary hover:bg-bg-accent disabled:opacity-50',
  // Acción destructiva.
  danger: 'bg-danger text-white hover:opacity-90 disabled:opacity-50',
};

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3.5 text-small',
  md: 'h-10 px-5 text-body',
  lg: 'h-12 px-7 text-body',
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

/** Botón reutilizable. Radio de 6px y sombra sutil, según docs/BRAND.md. */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-control font-medium',
        'disabled:cursor-not-allowed',
        // `press-feedback` (globals.css) baja el botón a 0.97 al pulsarlo —es lo
        // que hace que parezca que la interfaz ha oído el clic— y declara de paso
        // la transición de color. Va todo junto a propósito: son la misma
        // propiedad abreviada y separarlo hace que una pise a la otra.
        'press-feedback',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = 'Button';
