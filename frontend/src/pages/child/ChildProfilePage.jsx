import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { User, Sparkles } from 'lucide-react';

export function ChildProfilePage() {
  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Child Profile</h1>
          <p className="text-sm text-slate-500">Learner details and accommodation preferences.</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center font-bold text-xl">
                L
              </div>
              <div>
                <CardTitle>Leo Smith</CardTitle>
                <p className="text-xs text-slate-500">Role: Child Learner | Age: 8</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 pt-4 border-t border-slate-100 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-slate-400 block font-semibold">Learning Level</span>
                <span className="font-bold text-slate-800">Beginner (Visual Stage)</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block font-semibold">Special Needs Accommodation</span>
                <span className="font-bold text-slate-800">Visual Aids & Tactile Counters</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
