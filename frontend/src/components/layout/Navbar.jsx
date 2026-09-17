import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, Sparkles, BookOpen, ShieldCheck } from 'lucide-react';
import { authService } from '../../services/authService';

export function Navbar() {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'child':
        return <span className="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1"><Sparkles size={12}/> Child</span>;
      case 'parent':
        return <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1"><BookOpen size={12}/> Parent</span>;
      case 'admin':
        return <span className="bg-purple-100 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1"><ShieldCheck size={12}/> Admin</span>;
      default:
        return null;
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-30 px-6 flex items-center justify-between shadow-xs">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-[#2563EB] rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-sm">
          A
        </div>
        <div>
          <span className="font-bold text-slate-900 text-base leading-tight block">AdaptLearn</span>
          <span className="text-[11px] text-slate-500 hidden sm:block">Special Needs Learning System</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 py-1.5 px-3 rounded-lg">
            <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
              {user.full_name?.charAt(0) || 'U'}
            </div>
            <div className="text-left hidden md:block">
              <p className="text-xs font-semibold text-slate-800 leading-none">{user.full_name}</p>
              <div className="mt-1">{getRoleBadge(user.role)}</div>
            </div>
            <button 
              onClick={handleLogout}
              className="ml-2 text-slate-400 hover:text-red-600 transition-colors p-1.5 rounded-md hover:bg-slate-200"
              title="Logout"
              aria-label="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
