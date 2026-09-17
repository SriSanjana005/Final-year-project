import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className, 
  disabled, 
  ...props 
}) {
  const baseStyles = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none cursor-pointer";
  
  const variants = {
    primary: "bg-[#2563EB] text-white hover:bg-blue-700 shadow-sm",
    secondary: "bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-200",
    outline: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
    ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
    danger: "bg-red-600 text-white hover:bg-red-700 shadow-sm",
    success: "bg-[#14B8A6] text-white hover:bg-teal-700 shadow-sm",
  };

  const sizes = {
    sm: "h-8 px-3 text-xs",
    md: "h-10 px-4 text-sm min-h-[40px]",
    lg: "h-12 px-6 text-base min-h-[48px]", // Accessible large touch target
  };

  return (
    <button 
      className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
