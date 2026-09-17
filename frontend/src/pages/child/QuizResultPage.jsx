import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Award, ArrowRight, RefreshCw } from 'lucide-react';

export function QuizResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const score = location.state?.score || 100;

  return (
    <AppLayout>
      <div className="max-w-md mx-auto py-10 text-center space-y-6">
        <Card className="p-8 shadow-md">
          <CardContent className="space-y-6 pt-2">
            <div className="w-20 h-20 bg-teal-100 text-[#14B8A6] rounded-full flex items-center justify-center mx-auto shadow-sm">
              <Award size={44} />
            </div>

            <div>
              <h1 className="text-2xl font-bold text-slate-900">Great Job, Leo! 🎉</h1>
              <p className="text-slate-500 text-sm mt-1">Quiz Completed Successfully</p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <p className="text-xs text-slate-500 uppercase font-semibold">Your Score</p>
              <p className="text-4xl font-extrabold text-[#14B8A6] mt-1">{score}%</p>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg text-left text-xs text-blue-900 leading-relaxed">
              🤖 <strong>AI Feedback:</strong> Interaction data logged into Transformer history sequence. The DRL recommendation engine will adapt your next topic difficulty accordingly.
            </div>

            <div className="flex flex-col gap-3 pt-2">
              <Button variant="primary" size="lg" className="gap-2" onClick={() => navigate('/child/recommendations')}>
                View Next Recommended Activity <ArrowRight size={18} />
              </Button>
              <Button variant="outline" size="md" className="gap-2" onClick={() => navigate('/child/quiz')}>
                <RefreshCw size={16} /> Try Another Quiz
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
