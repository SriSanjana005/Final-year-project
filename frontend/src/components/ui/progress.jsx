import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Progress({ value = 0, max = 100, className, color = "bg-[#14B8A6]" }) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  return (
    <div 
      role="progressbar" 
      aria-valuenow={value} 
      aria-valuemin={0} 
      aria-valuemax={max}
      className={twMerge(clsx("w-full bg-slate-100 rounded-full h-3 overflow-hidden", className))}
    >
      <div 
        className={clsx("h-full transition-all duration-500 ease-out rounded-full", color)}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
