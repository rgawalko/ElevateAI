import React from 'react';
import { cn } from '../utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'default' | 'filled';
}

export const Input: React.FC<InputProps> = ({
  className,
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  variant = 'default',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = "flex h-10 w-full rounded-md border px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-secondary-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";
  
  const variantClasses = {
    default: "border-secondary-300 bg-white",
    filled: "border-secondary-200 bg-secondary-50"
  };

  const errorClasses = error 
    ? "border-danger-300 focus-visible:ring-danger-500" 
    : variantClasses[variant];

  return (
    <div className="space-y-2">
      {label && (
        <label 
          htmlFor={inputId}
          className="text-sm font-medium text-secondary-700"
        >
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400">
            {leftIcon}
          </div>
        )}
        
        <input
          id={inputId}
          className={cn(
            baseClasses,
            errorClasses,
            leftIcon && "pl-10",
            rightIcon && "pr-10",
            className
          )}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400">
            {rightIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-danger-600">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="text-sm text-secondary-500">
          {helperText}
        </p>
      )}
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'filled';
}

export const Textarea: React.FC<TextareaProps> = ({
  className,
  label,
  error,
  helperText,
  variant = 'default',
  id,
  ...props
}) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = "flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm ring-offset-background placeholder:text-secondary-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";
  
  const variantClasses = {
    default: "border-secondary-300 bg-white",
    filled: "border-secondary-200 bg-secondary-50"
  };

  const errorClasses = error 
    ? "border-danger-300 focus-visible:ring-danger-500" 
    : variantClasses[variant];

  return (
    <div className="space-y-2">
      {label && (
        <label 
          htmlFor={textareaId}
          className="text-sm font-medium text-secondary-700"
        >
          {label}
        </label>
      )}
      
      <textarea
        id={textareaId}
        className={cn(
          baseClasses,
          errorClasses,
          className
        )}
        {...props}
      />
      
      {error && (
        <p className="text-sm text-danger-600">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="text-sm text-secondary-500">
          {helperText}
        </p>
      )}
    </div>
  );
};

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'filled';
  options: Array<{ value: string; label: string; disabled?: boolean }>;
}

export const Select: React.FC<SelectProps> = ({
  className,
  label,
  error,
  helperText,
  variant = 'default',
  options,
  id,
  ...props
}) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = "flex h-10 w-full rounded-md border px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";
  
  const variantClasses = {
    default: "border-secondary-300 bg-white",
    filled: "border-secondary-200 bg-secondary-50"
  };

  const errorClasses = error 
    ? "border-danger-300 focus-visible:ring-danger-500" 
    : variantClasses[variant];

  return (
    <div className="space-y-2">
      {label && (
        <label 
          htmlFor={selectId}
          className="text-sm font-medium text-secondary-700"
        >
          {label}
        </label>
      )}
      
      <select
        id={selectId}
        className={cn(
          baseClasses,
          errorClasses,
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option 
            key={option.value} 
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="text-sm text-danger-600">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="text-sm text-secondary-500">
          {helperText}
        </p>
      )}
    </div>
  );
};
