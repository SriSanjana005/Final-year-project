import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { userService } from '../../services/userService';

export function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await userService.getUsers();
        setUsers(data);
      } catch (err) {
        console.error("Failed to fetch user list:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const getRoleBadge = (role) => {
    switch (role) {
      case 'child':
        return <Badge variant="success">Child</Badge>;
      case 'parent':
        return <Badge variant="default">Parent</Badge>;
      case 'admin':
        return <Badge variant="warning">Admin</Badge>;
      default:
        return <Badge variant="neutral">{role}</Badge>;
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
            <p className="text-sm text-slate-500">Live system user accounts and roles.</p>
          </div>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">System Users ({users.length})</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="p-4 text-center text-xs text-slate-400">Loading users...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">ID</th>
                      <th className="pb-3 px-2">Name</th>
                      <th className="pb-3 px-2">Email</th>
                      <th className="pb-3 px-2">Role</th>
                      <th className="pb-3 px-2">Status</th>
                      <th className="pb-3 px-2">Created Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 text-slate-400">#{u.id}</td>
                        <td className="py-3 px-2 font-semibold text-slate-800">{u.name}</td>
                        <td className="py-3 px-2 text-slate-600">{u.email}</td>
                        <td className="py-3 px-2">{getRoleBadge(u.role)}</td>
                        <td className="py-3 px-2">
                          <Badge variant={u.is_active ? "success" : "danger"}>
                            {u.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </td>
                        <td className="py-3 px-2 text-slate-500">
                          {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
