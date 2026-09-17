import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Sparkles, Brain, ArrowRight, Play } from 'lucide-react';

export function RecommendationsPage() {
  const navigate = useNavigate();

  const recommendations = [
    {
      id: 1,
      title: "Visual Block Addition Practice",
      topic: "Mathematics",
      difficulty: 1,
      confidence: "94%",
      drlAction: "Action 2: Maintain Same Difficulty Level",
      reason: "Transformer sequence vector detected consistent 85%+ scores on Level 1 visual addition."
    },
    {
      id: 2,
      title: "Interactive Word-Picture Matching",
      topic: "Reading",
      difficulty: 1,
      confidence: "88%",
      drlAction: "Action 4: Practice Activity Reinforcement",
      reason: "Reinforcing sight word comprehension before introducing multi-word sentences."
    }
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="text-[#2563EB]" /> Personalized Recommendations
          </h1>
          <p className="text-sm text-slate-500">Adaptive content selected based on your recent learning history.</p>
        </div>

        {/* AI System Architecture Banner */}
        <div className="bg-slate-900 text-white p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
            <Brain size={16} /> Transformer + DRL Recommendation Pipeline
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs pt-2">
            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <span className="text-blue-400 font-bold">1. Learning History</span>
              <p className="text-slate-400 mt-1">Tracks score, time spent, and interactions.</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <span className="text-blue-400 font-bold">2. Transformer</span>
              <p className="text-slate-400 mt-1">Encodes sequence history into state representation.</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <span className="text-blue-400 font-bold">3. PPO DRL Agent</span>
              <p className="text-slate-400 mt-1">Selects optimal next learning action (0-4).</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <span className="text-teal-400 font-bold">4. Recommended Content</span>
              <p className="text-slate-400 mt-1">Selects approved item from admin library.</p>
            </div>
          </div>
        </div>

        {/* Recommendations list */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations.map((rec) => (
            <Card key={rec.id} className="border-l-4 border-l-[#2563EB] flex flex-col justify-between">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <Badge variant="default">{rec.topic}</Badge>
                  <span className="text-xs font-bold text-teal-600">Match Confidence: {rec.confidence}</span>
                </div>
                <CardTitle className="text-lg pt-1">{rec.title}</CardTitle>
                <CardDescription>{rec.drlAction}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600">
                  🧠 <strong>Model Rationale:</strong> {rec.reason}
                </div>
                <Button 
                  variant="primary" 
                  size="md" 
                  className="w-full gap-2"
                  onClick={() => navigate('/child/content')}
                >
                  <Play size={16} /> Start Learning Content
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
