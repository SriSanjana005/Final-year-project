import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Plus } from 'lucide-react';

export function TopicManagementPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Topic Management</h1>
            <p className="text-sm text-slate-500">Maintain approved learning subjects and categories.</p>
          </div>
          <Button variant="primary" className="gap-2"><Plus size={16}/> Add Topic</Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Active Topics</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                <h4 className="font-bold text-slate-800">Mathematics - Addition & Subtraction</h4>
                <p className="text-xs text-slate-500 mt-1">Category: Mathematics | Modules: 5</p>
              </div>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                <h4 className="font-bold text-slate-800">Reading Comprehension & Sight Words</h4>
                <p className="text-xs text-slate-500 mt-1">Category: English | Modules: 4</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
