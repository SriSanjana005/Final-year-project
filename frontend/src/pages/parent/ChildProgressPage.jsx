import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { userService } from '../../services/userService';
import { progressService } from '../../services/progressService';
import { Loader2, TrendingUp, Award, Clock } from 'lucide-react';

export function ChildProgressPage() {
  const [children, setChildren] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState("");
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchingProgress, setFetchingProgress] = useState(false);

  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const data = await userService.getParentChildren();
        setChildren(data);
        if (data.length > 0) {
          setSelectedChildId(data[0].id.toString());
        }
      } catch (err) {
        console.error("Failed to load parent's children:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchChildren();
  }, []);

  useEffect(() => {
    if (!selectedChildId) return;
    const fetchProgress = async () => {
      setFetchingProgress(true);
      try {
        const data = await progressService.getChildProgress(selectedChildId);
        setProgressData(data);
      } catch (err) {
        console.error("Failed to load child progress:", err);
      } finally {
        setFetchingProgress(false);
      }
    };
    fetchProgress();
  }, [selectedChildId]);

  const selectedChildObj = children.find(c => c.id.toString() === selectedChildId);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Child Progress Report</h1>
            <p className="text-sm text-slate-500">Comprehensive breakdown of topic mastery and performance metrics.</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-500">Select Child:</span>
            {loading ? (
              <span className="text-xs text-slate-400">Loading...</span>
            ) : children.length === 0 ? (
              <span className="text-xs text-amber-600 font-semibold bg-amber-50 px-2 py-1 rounded">No linked children</span>
            ) : (
              <select 
                value={selectedChildId} 
                onChange={(e) => setSelectedChildId(e.target.value)}
                className="h-10 px-3 bg-slate-50 border border-slate-300 rounded-lg text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {children.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.user?.name || `Child #${c.id}`} ({c.learning_level})
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {fetchingProgress ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="animate-spin text-blue-600" size={32} />
          </div>
        ) : progressData ? (
          <>
            {/* Overview Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center font-bold">
                  <TrendingUp size={24} />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Average Score</p>
                  <p className="text-2xl font-extrabold text-slate-900">
                    {Math.round(progressData.average_score || 0)}%
                  </p>
                </div>
              </Card>

              <Card className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-teal-50 text-teal-600 rounded-xl flex items-center justify-center font-bold">
                  <Award size={24} />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Total Attempts</p>
                  <p className="text-2xl font-extrabold text-slate-900">
                    {progressData.total_quizzes_attempted || 0}
                  </p>
                </div>
              </Card>

              <Card className="p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center font-bold">
                  <Clock size={24} />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Performance Tier</p>
                  <p className="text-xl font-extrabold text-purple-700 capitalize">
                    {progressData.performance_tier || 'Beginner'}
                  </p>
                </div>
              </Card>
            </div>

            {/* Topic Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Topic Mastery Breakdown</CardTitle>
                <CardDescription>Average performance per topic for {selectedChildObj?.user?.name || 'Child'}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {progressData.topic_breakdown?.length === 0 ? (
                  <p className="text-xs text-slate-500 text-center py-6">No quiz topic data recorded yet.</p>
                ) : (
                  progressData.topic_breakdown?.map((tb) => (
                    <div key={tb.topic_id} className="space-y-1">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-800 font-bold">{tb.topic_name}</span>
                        <span className="text-blue-600 font-bold">{Math.round(tb.avg_score)}% ({tb.attempts_count} attempts)</span>
                      </div>
                      <Progress value={tb.avg_score} color={tb.avg_score >= 80 ? 'bg-teal-500' : tb.avg_score >= 50 ? 'bg-blue-500' : 'bg-amber-500'} />
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          <div className="text-center py-12 text-slate-500 text-sm">
            Select a child above to view their progress data.
          </div>
        )}
      </div>
    </AppLayout>
  );
}

