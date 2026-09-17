import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Plus } from 'lucide-react';

export function QuestionManagementPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Question Bank</h1>
            <p className="text-sm text-slate-500">Manage individual assessment questions and difficulty tags.</p>
          </div>
          <Button variant="primary" className="gap-2"><Plus size={16}/> Add Question</Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Question Items</CardTitle></CardHeader>
          <CardContent>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm">
              <p className="font-bold text-slate-800">"What is 4 + 3?"</p>
              <p className="text-xs text-slate-500 mt-1">Difficulty Level: 1 | Visual Options: Yes</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
