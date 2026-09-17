import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Progress } from '../../components/ui/progress';

export function ChildProgressPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Child Progress Detailed Report</h1>
          <p className="text-sm text-slate-500">Comprehensive breakdown of topic mastery for Leo Smith.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle className="text-base">Mathematics Mastery</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1"><span>Addition with Counters</span><span>85%</span></div>
                <Progress value={85} />
              </div>
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1"><span>Subtraction Concepts</span><span>50%</span></div>
                <Progress value={50} color="bg-amber-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-base">Language & Reading</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1"><span>Sight Words Matching</span><span>70%</span></div>
                <Progress value={70} color="bg-[#2563EB]" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
