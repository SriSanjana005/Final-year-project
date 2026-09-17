import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Plus } from 'lucide-react';

export function QuizManagementPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Quiz Management</h1>
            <p className="text-sm text-slate-500">Configure quiz assessments per topic.</p>
          </div>
          <Button variant="primary" className="gap-2"><Plus size={16}/> Create Quiz</Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Configured Quizzes</CardTitle></CardHeader>
          <CardContent>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm">
              <span className="font-bold text-slate-800">Basic Shapes & Addition Assessment</span>
              <p className="text-xs text-slate-500 mt-1">Passing Threshold: 70% | Questions: 5</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
