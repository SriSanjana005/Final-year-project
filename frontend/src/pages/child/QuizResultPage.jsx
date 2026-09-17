import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Award, ArrowRight, RefreshCw, TrendingUp } from 'lucide-react';

export function QuizResultPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const result = location.state?.result || {
    score: 4,
    total_questions: 5,
    correct_answers: 4,
    percentage: 80.0,
    time_taken: 120,
    performance: 'good'
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins} min ${secs} sec` : `${secs} sec`;
  };

  const getPerformanceBadge = (perf) => {
    switch (perf) {
      case 'excellent':
        return <Badge variant="success" className="text-sm px-3 py-1">Excellent Mastery! 🎉</Badge>;
      case 'good':
        return <Badge variant="default" className="text-sm px-3 py-1">Good Job! 👍</Badge>;
      default:
        return <Badge variant="warning" className="text-sm px-3 py-1">Needs Practice 💪</Badge>;
    }
  };

  return (
    <AppLayout>
      <div className="max-w-md mx-auto py-8 text-center space-y-6">
        <Card className="p-8 shadow-md border border-slate-200">
          <CardContent className="space-y-6 pt-2">
            <div className="w-20 h-20 bg-teal-100 text-[#14B8A6] rounded-full flex items-center justify-center mx-auto shadow-sm">
              <Award size={44} />
            </div>

            <div>
              <h1 className="text-2xl font-bold text-slate-900">Quiz Completed!</h1>
              <div className="mt-2">{getPerformanceBadge(result.performance)}</div>
            </div>

            {/* Score Breakdown Box */}
            <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
              <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Final Score</span>
              <p className="text-5xl font-extrabold text-[#14B8A6]">{result.percentage}%</p>
              
              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-200 text-xs">
                <div>
                  <span className="text-slate-400 block font-medium">Correct Answers</span>
                  <span className="font-bold text-slate-800 text-sm">{result.correct_answers} / {result.total_questions}</span>
                </div>
                <div>
                  <span className="text-slate-400 block font-medium">Time Taken</span>
                  <span className="font-bold text-slate-800 text-sm">{formatTime(result.time_taken)}</span>
                </div>
              </div>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg text-left text-xs text-blue-900 leading-relaxed">
              📊 <strong>Performance Recorded:</strong> Attempt data logged into database history. Used to track long-term learning trajectory.
            </div>

            <div className="flex flex-col gap-3 pt-2">
              <Button variant="primary" size="lg" className="gap-2 font-semibold" onClick={() => navigate('/child/progress')}>
                <TrendingUp size={18} /> View My Progress
              </Button>
              <Button variant="outline" size="md" className="gap-2 text-xs" onClick={() => navigate('/child/quiz')}>
                <RefreshCw size={16} /> Take Another Quiz
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
