import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Home } from 'lucide-react';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center items-center p-6 text-center">
      <h1 className="text-6xl font-extrabold text-[#2563EB]">404</h1>
      <h2 className="text-2xl font-bold text-slate-900 mt-2">Page Not Found</h2>
      <p className="text-slate-500 text-sm max-w-sm mt-2 mb-6">
        The page you are looking for does not exist or has been moved.
      </p>
      <Button variant="primary" onClick={() => navigate('/login')} className="gap-2">
        <Home size={16} /> Back to Sign In
      </Button>
    </div>
  );
}
