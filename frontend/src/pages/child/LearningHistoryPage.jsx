import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';

export function LearningHistoryPage() {
  const history = [
    { date: "2026-09-17 10:30", activity: "Quiz: Shapes & Colors", score: "85%", status: "Completed", timeSpent: "4 mins" },
    { date: "2026-09-16 15:15", activity: "Lesson: Visual Block Counting", score: "100%", status: "Completed", timeSpent: "6 mins" },
    { date: "2026-09-15 16:00", activity: "Lesson: Sight Words Reading", score: "70%", status: "Completed", timeSpent: "5 mins" },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Learning History</h1>
          <p className="text-sm text-slate-500">Recorded sequential interaction logs used by the Transformer model.</p>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Interaction Sequence Log</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                    <th className="pb-3 px-2">Timestamp</th>
                    <th className="pb-3 px-2">Activity / Topic</th>
                    <th className="pb-3 px-2">Duration</th>
                    <th className="pb-3 px-2">Score</th>
                    <th className="pb-3 px-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((row, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="py-3 px-2 text-slate-500">{row.date}</td>
                      <td className="py-3 px-2 font-semibold text-slate-800">{row.activity}</td>
                      <td className="py-3 px-2 text-slate-600">{row.timeSpent}</td>
                      <td className="py-3 px-2 font-bold text-teal-600">{row.score}</td>
                      <td className="py-3 px-2"><Badge variant="success">{row.status}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
