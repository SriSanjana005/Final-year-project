import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';

export function ChildLearningHistoryPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Child Learning Activity History</h1>
          <p className="text-sm text-slate-500">Timeline of Leo Smith's learning activities and recommendations.</p>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Recent Activities</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { title: "Quiz: Visual Shapes", score: "85%", date: "Today, 10:30 AM" },
                { title: "Lesson: Visual Addition", score: "100%", date: "Yesterday, 3:15 PM" },
              ].map((item, i) => (
                <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center text-sm">
                  <div>
                    <p className="font-semibold text-slate-800">{item.title}</p>
                    <span className="text-xs text-slate-400">{item.date}</span>
                  </div>
                  <Badge variant="success">{item.score}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
