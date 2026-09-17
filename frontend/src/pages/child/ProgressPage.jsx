import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Progress } from '../../components/ui/progress';

export function ProgressPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">My Learning Progress</h1>
          <p className="text-sm text-slate-500">Track your completed topics and quiz achievements.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle className="text-base">Mathematics Progress</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-xs font-semibold"><span>Level 1: Visual Addition</span><span>80%</span></div>
              <Progress value={80} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-base">Reading Comprehension</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-xs font-semibold"><span>Sight Words & Matching</span><span>60%</span></div>
              <Progress value={60} color="bg-[#2563EB]" />
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
