import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Plus } from 'lucide-react';

export function ContentManagementPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Educational Content Library</h1>
            <p className="text-sm text-slate-500">Admin-approved learning material for DRL content pool.</p>
          </div>
          <Button variant="primary" className="gap-2"><Plus size={16}/> Create Content</Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Approved Content Pool</CardTitle></CardHeader>
          <CardContent>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm">
              <span className="font-bold text-slate-800">Visual Block Addition (Difficulty Level 1)</span>
              <p className="text-xs text-slate-500 mt-1">Status: Approved for AI Recommendation Engine</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
