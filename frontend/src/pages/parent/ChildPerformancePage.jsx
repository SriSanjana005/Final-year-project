import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export function ChildPerformancePage() {
  const trendData = [
    { session: 'Quiz 1', score: 60 },
    { session: 'Quiz 2', score: 75 },
    { session: 'Quiz 3', score: 70 },
    { session: 'Quiz 4', score: 85 },
    { session: 'Quiz 5', score: 90 },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Quiz Performance Trends</h1>
          <p className="text-sm text-slate-500">Score history trajectory logged for deep learning analysis.</p>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Historical Score Trajectory</CardTitle></CardHeader>
          <CardContent>
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="session" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="score" stroke="#14B8A6" strokeWidth={3} dot={{ r: 5 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
