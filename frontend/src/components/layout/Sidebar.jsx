import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, BookOpen, HelpCircle, TrendingUp, 
  Sparkles, History, User, Users, FolderKanban, 
  FileText, HelpCircle as QuestionIcon, Network, Cpu
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Sidebar() {
  const { user } = useAuth();
  const role = user?.role || 'child';

  const childLinks = [
    { to: '/child/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/child/content', label: 'Learning Topics', icon: BookOpen },
    { to: '/child/quiz', label: 'Practice Quiz', icon: HelpCircle },
    { to: '/child/recommendations', label: 'Recommendations', icon: Sparkles },
    { to: '/child/progress', label: 'My Progress', icon: TrendingUp },
    { to: '/child/history', label: 'Learning History', icon: History },
    { to: '/child/profile', label: 'Profile', icon: User },
  ];

  const parentLinks = [
    { to: '/parent/dashboard', label: 'Parent Dashboard', icon: LayoutDashboard },
    { to: '/parent/child-progress', label: 'Child Progress', icon: TrendingUp },
    { to: '/parent/child-performance', label: 'Quiz Performance', icon: HelpCircle },
    { to: '/parent/child-history', label: 'Activity History', icon: History },
    { to: '/parent/profile', label: 'Parent Profile', icon: User },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Admin Overview', icon: LayoutDashboard },
    { to: '/admin/users', label: 'User Management', icon: Users },
    { to: '/admin/mapping', label: 'Parent-Child Links', icon: Network },
    { to: '/admin/topics', label: 'Topic Management', icon: FolderKanban },
    { to: '/admin/content', label: 'Educational Content', icon: FileText },
    { to: '/admin/quizzes', label: 'Quiz Management', icon: HelpCircle },
    { to: '/admin/questions', label: 'Question Bank', icon: QuestionIcon },
    { to: '/admin/recommendations', label: 'Recommendations Baseline', icon: Sparkles },
  ];

  const links = role === 'admin' ? adminLinks : role === 'parent' ? parentLinks : childLinks;

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between py-6 px-4 shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="px-3">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {role.toUpperCase()} MENU
          </p>
        </div>
        <nav className="space-y-1">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-[#2563EB] border border-blue-100 shadow-2xs font-semibold'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                <Icon size={18} />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
          <Cpu size={14} className="text-[#2563EB]" />
          <span>AI Architecture</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-normal">
          Transformer Representation + DRL Agent ready for future ML backend binding.
        </p>
      </div>
    </aside>
  );
}
