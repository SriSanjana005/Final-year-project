import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Badge({ children, variant = 'default', className }) {
  const variants = {
    default: "bg-blue-50 text-blue-700 border-blue-200",
    success: "bg-teal-50 text-teal-700 border-teal-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    danger: "bg-red-50 text-red-700 border-red-200",
    neutral: "bg-slate-100 text-slate-700 border-slate-200",
  };

  return (
    <span className={twMerge(clsx("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border", variants[variant], className))}>
      {children}
    </span>
  );
}
