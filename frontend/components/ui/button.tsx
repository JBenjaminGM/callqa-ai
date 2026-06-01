import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variants: Record<Variant, string> = {
  // Acción primaria: relleno Índigo con resplandor en hover.
  primary:
    'bg-accent-primary text-white hover:shadow-[0_0_24px_var(--glow)] disabled:opacity-50',
  // Secundaria: estilo cristal con borde fino.
  secondary:
    'glass text-text-primary hover:border-accent-primary disabled:opacity-50',
  ghost:
    'bg-transparent text-text-primary hover:bg-bg-accent/50 disabled:opacity-50',
  danger:
    'bg-danger text-white hover:shadow-[0_0_24px_rgba(225,29,72,0.4)] disabled:opacity-50',
};

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3 text-small',
  md: 'h-10 px-4 text-body',
  lg: 'h-12 px-6 text-body',
};

/** Botón reutilizable con las variantes del sistema de diseño Aetheric. */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium',
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
