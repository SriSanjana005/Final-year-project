import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';

export function ParentProfilePage() {
  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Parent Profile</h1>
          <p className="text-sm text-slate-500">Account settings and child links.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Sarah Smith</CardTitle>
            <p className="text-xs text-slate-500">Role: Parent | Email: parent@learning.com</p>
          </CardHeader>
          <CardContent className="space-y-4 pt-4 border-t border-slate-100 text-sm">
            <div>
              <span className="text-xs text-slate-400 font-semibold block">Linked Children</span>
              <p className="font-bold text-slate-800">1. Leo Smith (Age 8)</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
