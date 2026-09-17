import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Plus } from 'lucide-react';

export function UserManagementPage() {
  const users = [
    { id: 1, name: "Leo Smith", email: "child@learning.com", role: "child", status: "Active" },
    { id: 2, name: "Sarah Smith", email: "parent@learning.com", role: "parent", status: "Active" },
    { id: 3, name: "Dr. Alex Rivera", email: "admin@learning.com", role: "admin", status: "Active" }
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
            <p className="text-sm text-slate-500">Manage user accounts and role assignments.</p>
          </div>
          <Button variant="primary" className="gap-2"><Plus size={16}/> Add User</Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">System Users</CardTitle></CardHeader>
          <CardContent>
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                  <th className="pb-3">Name</th>
                  <th className="pb-3">Email</th>
                  <th className="pb-3">Role</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50">
                    <td className="py-3 font-semibold text-slate-800">{u.name}</td>
                    <td className="py-3 text-slate-500">{u.email}</td>
                    <td className="py-3"><Badge variant="default">{u.role}</Badge></td>
                    <td className="py-3"><Badge variant="success">{u.status}</Badge></td>
                    <td className="py-3 text-right">
                      <Button variant="ghost" size="sm">Edit</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
