import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Users, FolderKanban, FileText, HelpCircle, Network, ShieldCheck, ArrowRight } from 'lucide-react';

export function AdminDashboard() {
  const navigate = useNavigate();

  const metrics = [
    { title: "Total Users", count: "14", icon: Users, color: "text-blue-600 bg-blue-50" },
    { title: "Total Children", count: "8", icon: Users, color: "text-teal-600 bg-teal-50" },
    { title: "Total Parents", count: "5", icon: Users, color: "text-indigo-600 bg-indigo-50" },
    { title: "Approved Content", count: "24", icon: FileText, color: "text-purple-600 bg-purple-50" },
    { title: "Total Quizzes", count: "12", icon: HelpCircle, color: "text-amber-600 bg-amber-50" },
  ];

  const adminNav = [
    { label: "User Management", path: "/admin/users", icon: Users },
    { label: "Parent-Child Mapping", path: "/admin/mapping", icon: Network },
    { label: "Topic Management", path: "/admin/topics", icon: FolderKanban },
    { label: "Content Management", path: "/admin/content", icon: FileText },
    { label: "Quiz Management", path: "/admin/quizzes", icon: HelpCircle },
    { label: "Question Bank", path: "/admin/questions", icon: HelpCircle },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="text-purple-600" /> Admin Control Center
          </h1>
          <p className="text-sm text-slate-500">Manage educational content library, approved topics, users, and mappings.</p>
        </div>

        {/* System Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {metrics.map((m, i) => {
            const Icon = m.icon;
            return (
              <Card key={i} className="p-4 space-y-2">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${m.color}`}>
                  <Icon size={20} />
                </div>
                <div>
                  <p className="text-[11px] text-slate-500 font-semibold uppercase">{m.title}</p>
                  <p className="text-2xl font-extrabold text-slate-900">{m.count}</p>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Management Quick Navigation */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Content & User Administration</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {adminNav.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div 
                  key={idx}
                  onClick={() => navigate(item.path)}
                  className="p-5 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-sm transition-all cursor-pointer flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-slate-100 group-hover:bg-blue-50 text-slate-700 group-hover:text-blue-600 rounded-lg flex items-center justify-center transition-colors">
                      <Icon size={20} />
                    </div>
                    <span className="font-bold text-slate-800 text-sm group-hover:text-blue-600 transition-colors">{item.label}</span>
                  </div>
                  <ArrowRight size={18} className="text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent System Activity Log */}
        <Card>
          <CardHeader><CardTitle className="text-base">Recent Administrative Activity</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center">
                <span>Created new approved content item: <strong>"Visual Block Addition"</strong></span>
                <span className="text-slate-400">1 hour ago</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center">
                <span>Mapped Parent <strong>Sarah Smith</strong> to Child <strong>Leo Smith</strong></span>
                <span className="text-slate-400">Yesterday</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
