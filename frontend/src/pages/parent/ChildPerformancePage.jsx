import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { userService } from '../../services/userService';
import { progressService } from '../../services/progressService';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Loader2 } from 'lucide-react';

export function ChildPerformancePage() {
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
        console.error("Failed to load children:", err);
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
        console.error("Failed to load child performance:", err);
      } finally {
        setFetchingProgress(false);
      }
    };
    fetchProgress();
  }, [selectedChildId]);

  const selectedChildObj = children.find(c => c.id.toString() === selectedChildId);

  const chartData = (progressData?.recent_attempts || []).slice().reverse().map((att, index) => ({
    session: `Quiz #${att.quiz_id} (${new Date(att.completed_at).toLocaleDateString()})`,
    score: Math.round(att.percentage_score),
    tier: att.performance_tier
  }));

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Quiz Performance Trends</h1>
            <p className="text-sm text-slate-500">Score history trajectory logged for deep learning analysis.</p>
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

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Historical Score Trajectory</CardTitle>
            <CardDescription>Performance progression for {selectedChildObj?.user?.name || 'Selected Learner'}</CardDescription>
          </CardHeader>
          <CardContent>
            {fetchingProgress ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="animate-spin text-blue-600" size={32} />
              </div>
            ) : chartData.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">
                No quiz attempt data recorded for this child yet.
              </div>
            ) : (
              <div className="h-72 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis dataKey="session" tick={{ fontSize: 11, fill: '#64748B' }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#64748B' }} />
                    <Tooltip 
                      formatter={(value) => [`${value}%`, 'Score']}
                      contentStyle={{ backgroundColor: '#1E293B', borderRadius: '8px', color: '#FFF' }}
                    />
                    <Line type="monotone" dataKey="score" stroke="#14B8A6" strokeWidth={3} dot={{ r: 6, fill: '#0D9488' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}

