import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  icon,
  iconPosition = 'left',
  ...props
}) => {
  const baseClasses = "inline-flex items-center justify-center transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background hover:scale-105 active:scale-95";
  const fontClasses = "font-sans font-semibold"; // Inter 600

  const variantClasses = {
    primary: "text-white shadow-lg hover:shadow-xl transition-all duration-200",
    secondary: "shadow-md hover:shadow-lg transition-all duration-200",
    accent: "text-white shadow-lg hover:shadow-xl transition-all duration-200",
    outline: "border-2 bg-transparent shadow-sm hover:shadow-md transition-all duration-200",
    ghost: "transition-all duration-200",
    danger: "text-white shadow-lg hover:shadow-xl transition-all duration-200"
  };

  const sizeClasses = {
    sm: "h-9 px-4 text-sm rounded-xl",
    md: "h-11 px-6 text-sm rounded-xl",
    lg: "h-13 px-8 text-base rounded-xl"
  };

  const isDisabled = disabled || loading;

  const getButtonClasses = () => {
    const baseClasses = "btn hover-lift click-down";

    switch (variant) {
      case 'primary':
        return baseClasses;
      case 'secondary':
        return `${baseClasses} btn-secondary`;
      case 'accent':
        return `${baseClasses} btn-secondary`;
      case 'outline':
        return `${baseClasses} btn-outline`;
      case 'ghost':
        return "hover-lift click-down bg-transparent border-none text-primary-500 hover:bg-primary-50";
      case 'danger':
        return `${baseClasses} !bg-red-500 hover:!bg-red-600`;
      default:
        return baseClasses;
    }
  };

  return (
    <button
      className={cn(
        getButtonClasses(),
        sizeClasses[size],
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      )}
      
      {!loading && icon && iconPosition === 'left' && (
        <span className="mr-2">{icon}</span>
      )}
      
      {children}
      
      {!loading && icon && iconPosition === 'right' && (
        <span className="ml-2">{icon}</span>
      )}
    </button>
  );
};

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon: React.ReactNode;
}

export const IconButton: React.FC<IconButtonProps> = ({
  className,
  variant = 'ghost',
  size = 'md',
  loading = false,
  disabled,
  icon,
  ...props
}) => {
  const baseClasses = "inline-flex items-center justify-center font-sans font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background";
  
  const variantClasses = {
    primary: "text-white transition-all duration-200",
    secondary: "transition-all duration-200",
    accent: "text-white transition-all duration-200",
    outline: "border bg-transparent transition-all duration-200",
    ghost: "transition-all duration-200",
    danger: "text-white transition-all duration-200"
  };
  
  const sizeClasses = {
    sm: "h-8 w-8 rounded-md",
    md: "h-10 w-10 rounded-md",
    lg: "h-12 w-12 rounded-lg"
  };

  const isDisabled = disabled || loading;

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        icon
      )}
    </button>
  );
};
