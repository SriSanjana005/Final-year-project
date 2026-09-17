import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { useAuth } from '../../context/AuthContext';
import { progressService } from '../../services/progressService';
import { userService } from '../../services/userService';
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { TrendingUp, Award, HelpCircle, CheckCircle2 } from 'lucide-react';

export function ProgressPage() {
  const { user } = useAuth();
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        setLoading(true);
        // Get child profile first
        const childProf = await userService.getChildProfile();
        if (childProf) {
          const pData = await progressService.getChildProgress(childProf.id);
          setProgressData(pData);
        }
      } catch (err) {
        console.error("Failed to fetch progress data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
  }, []);

  const scoreTrendData = progressData?.recent_attempts
    ?.slice()
    ?.reverse()
    ?.map((att, idx) => ({
      session: `Quiz #${idx + 1}`,
      percentage: att.percentage,
      topic: att.topic_name
    })) || [];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <TrendingUp className="text-[#2563EB]" /> My Learning Progress
          </h1>
          <p className="text-sm text-slate-500">Live database metrics for {user?.name || 'Child Learner'}.</p>
        </div>

        {/* Overview Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-50 text-[#2563EB] rounded-xl flex items-center justify-center font-bold">
              <Award size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Overall Average Score</p>
              <p className="text-2xl font-extrabold text-slate-900">
                {loading ? "..." : `${progressData?.overall_average_percentage || 0}%`}
              </p>
            </div>
          </Card>

          <Card className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-teal-50 text-[#14B8A6] rounded-xl flex items-center justify-center font-bold">
              <HelpCircle size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Quizzes Completed</p>
              <p className="text-2xl font-extrabold text-slate-900">
                {loading ? "..." : progressData?.total_quizzes_completed || 0}
              </p>
            </div>
          </Card>

          <Card className="p-4 flex items-center gap-4 sm:col-span-2 lg:col-span-1">
            <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center font-bold">
              <CheckCircle2 size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Active Topics Mastered</p>
              <p className="text-2xl font-extrabold text-slate-900">
                {loading ? "..." : progressData?.topic_performances?.length || 0}
              </p>
            </div>
          </Card>
        </div>

        {/* Recharts Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Score Trajectory Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quiz Score Trajectory Trend</CardTitle>
              <CardDescription>Historical percentage trajectory across attempts</CardDescription>
            </CardHeader>
            <CardContent>
              {scoreTrendData.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">No attempt trajectory data logged yet. Complete a quiz to view chart!</div>
              ) : (
                <div className="h-64 w-full pt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={scoreTrendData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                      <XAxis dataKey="session" tick={{ fontSize: 11, fill: '#64748B' }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748B' }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="percentage" stroke="#14B8A6" strokeWidth={3} dot={{ r: 5 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Topic Average Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Topic-Wise Average Performance</CardTitle>
              <CardDescription>Breakdown by educational topic domain</CardDescription>
            </CardHeader>
            <CardContent>
              {!progressData?.topic_performances || progressData.topic_performances.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">No topic data logged yet.</div>
              ) : (
                <div className="h-64 w-full pt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={progressData.topic_performances}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                      <XAxis dataKey="topic_name" tick={{ fontSize: 11, fill: '#64748B' }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748B' }} />
                      <Tooltip cursor={{ fill: '#F1F5F9' }} />
                      <Bar dataKey="average_percentage" fill="#2563EB" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Attempts Log */}
        <Card>
          <CardHeader><CardTitle className="text-base">Recent Quiz Attempt Log</CardTitle></CardHeader>
          <CardContent>
            {!progressData?.recent_attempts || progressData.recent_attempts.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-400">No completed quiz attempts recorded yet.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">Quiz Title</th>
                      <th className="pb-3 px-2">Topic</th>
                      <th className="pb-3 px-2">Difficulty</th>
                      <th className="pb-3 px-2">Score</th>
                      <th className="pb-3 px-2">Percentage</th>
                      <th className="pb-3 px-2">Completed Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {progressData.recent_attempts.map((att) => (
                      <tr key={att.attempt_id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-slate-800">{att.quiz_title}</td>
                        <td className="py-3 px-2 text-slate-600">{att.topic_name}</td>
                        <td className="py-3 px-2 capitalize">{att.difficulty}</td>
                        <td className="py-3 px-2 font-semibold text-slate-700">{att.score} / {att.total_questions}</td>
                        <td className="py-3 px-2 font-bold text-teal-600">{att.percentage}%</td>
                        <td className="py-3 px-2 text-slate-500">
                          {att.completed_at ? new Date(att.completed_at).toLocaleString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
