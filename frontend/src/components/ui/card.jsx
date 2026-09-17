import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Card({ className, children, ...props }) {
  return (
    <div 
      className={twMerge(clsx("bg-white rounded-xl border border-slate-200 shadow-sm p-6 text-[#0F172A]", className))} 
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children, ...props }) {
  return <div className={twMerge(clsx("mb-4 flex flex-col space-y-1.5", className))} {...props}>{children}</div>;
}

export function CardTitle({ className, children, ...props }) {
  return <h3 className={twMerge(clsx("text-xl font-bold tracking-tight text-[#0F172A]", className))} {...props}>{children}</h3>;
}

export function CardDescription({ className, children, ...props }) {
  return <p className={twMerge(clsx("text-sm text-slate-500", className))} {...props}>{children}</p>;
}

export function CardContent({ className, children, ...props }) {
  return <div className={twMerge(clsx("pt-0", className))} {...props}>{children}</div>;
}

export function CardFooter({ className, children, ...props }) {
  return <div className={twMerge(clsx("flex items-center pt-4 border-t border-slate-100 mt-4", className))} {...props}>{children}</div>;
}
