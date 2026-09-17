import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { useAuth } from '../../context/AuthContext';
import { recommendationService } from '../../services/recommendationService';
import { Play, Sparkles, Award, ArrowRight, CheckCircle2, Loader2 } from 'lucide-react';

export function ChildDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentRec, setCurrentRec] = useState(null);
  const [loadingRec, setLoadingRec] = useState(true);

  useEffect(() => {
    const fetchRec = async () => {
      try {
        const data = await recommendationService.getCurrentRecommendation();
        setCurrentRec(data);
      } catch (err) {
        console.error("Failed to load dashboard recommendation:", err);
      } finally {
        setLoadingRec(false);
      }
    };
    fetchRec();
  }, []);

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Welcome & Progress Overview */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 md:p-8 text-white shadow-md">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="space-y-2">
              <span className="bg-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full inline-block">
                Welcome back, {user?.name || 'Learner'}! 👋
              </span>
              <h1 className="text-2xl md:text-3xl font-bold">Ready to continue your learning adventure?</h1>
              <p className="text-blue-100 text-sm">Adaptive rule-based learning modules ready for you today.</p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-xs p-4 rounded-xl border border-white/20 w-full md:w-72 space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span>Overall Learning Progress</span>
                <span>68%</span>
              </div>
              <Progress value={68} className="bg-blue-950/30" color="bg-[#14B8A6]" />
            </div>
          </div>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border-l-4 border-l-[#2563EB]">
            <CardHeader>
              <div className="flex justify-between items-center">
                <Badge variant="default">Learning Library</Badge>
                <span className="text-xs text-slate-400">All Topics</span>
              </div>
              <CardTitle className="text-lg pt-1">Explore Approved Content</CardTitle>
              <CardDescription>Browse all lessons and visual learning materials</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-xs text-slate-600">Access curated reading, math, and visual recognition exercises.</p>
              <Button 
                variant="primary" 
                size="lg" 
                className="w-full gap-2 font-bold" 
                onClick={() => navigate('/child/content')}
              >
                <Play size={18} /> Browse Content
              </Button>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-[#14B8A6] bg-teal-50/20">
            <CardHeader>
              <div className="flex justify-between items-center">
                <Badge variant="success" className="gap-1">
                  <Sparkles size={12} /> Recommended For You
                </Badge>
                <span className="text-xs font-medium text-teal-700 capitalize">
                  {currentRec?.difficulty || 'easy'}
                </span>
              </div>
              <CardTitle className="text-lg pt-1">
                {loadingRec ? "Loading recommendation..." : currentRec?.content_title || "Recommended Module"}
              </CardTitle>
              <CardDescription>
                Topic: {currentRec?.topic_name || 'General'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-xs text-slate-600 bg-white p-3 rounded-lg border border-slate-200">
                💡 <strong>Why this was recommended:</strong> {currentRec?.reason || "Based on your recent performance baseline."}
              </p>
              <Button 
                variant="success" 
                size="lg" 
                className="w-full gap-2 font-bold"
                onClick={() => {
                  if (currentRec) {
                    navigate(`/child/learning/${currentRec.content_id}`);
                  } else {
                    navigate('/child/recommendations');
                  }
                }}
              >
                Start Recommended Activity <ArrowRight size={18} />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Recent Performance & Learning Activity */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Award className="text-amber-500" size={18} /> Recent Quiz Score
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-center space-y-1">
                <span className="text-3xl font-extrabold text-slate-900">85%</span>
                <p className="text-xs font-semibold text-teal-600">PASSED</p>
                <p className="text-xs text-slate-500">Topic: Basic Shapes Identification</p>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full text-xs" 
                onClick={() => navigate('/child/quiz')}
              >
                Take a New Quiz
              </Button>
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Recent Learning Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { title: "Completed 'Visual Shapes & Colors' Quiz", time: "Today, 10:30 AM", score: "85%", status: "Completed" },
                  { title: "Read 'Counting Blocks' Interactive Lesson", time: "Yesterday, 3:15 PM", score: "100%", status: "Completed" },
                  { title: "Started 'Reading Sight Words'", time: "Sep 15, 4:00 PM", score: "In Progress", status: "Active" },
                ].map((act, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-50 border border-slate-100 rounded-lg text-sm">
                    <div className="flex items-center gap-3">
                      <CheckCircle2 size={18} className="text-[#14B8A6]" />
                      <div>
                        <p className="font-semibold text-slate-800 text-xs md:text-sm">{act.title}</p>
                        <span className="text-[11px] text-slate-400">{act.time}</span>
                      </div>
                    </div>
                    <Badge variant={act.status === 'Completed' ? 'success' : 'default'}>{act.score}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
