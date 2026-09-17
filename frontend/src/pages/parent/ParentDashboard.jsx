import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { userService } from '../../services/userService';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Users, TrendingUp, Sparkles, Award, Clock } from 'lucide-react';

export function ParentDashboard() {
  const [children, setChildren] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const data = await userService.getParentChildren();
        setChildren(data);
        if (data.length > 0) {
          setSelectedChildId(data[0].id.toString());
        }
      } catch (err) {
        console.error("Failed to fetch parent's linked children:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchChildren();
  }, []);

  const selectedChildObj = children.find(c => c.id.toString() === selectedChildId);

  const performanceData = [
    { topic: 'Math Addition', score: 85 },
    { topic: 'Sight Words', score: 70 },
    { topic: 'Shape Matching', score: 95 },
    { topic: 'Patterns', score: 80 },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Parent Header & Child Selector */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Parent Dashboard</h1>
            <p className="text-sm text-slate-500">Monitor your child's adaptive learning journey and AI recommendations.</p>
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

        {/* Selected Child Info Banner */}
        {selectedChildObj && (
          <div className="p-4 bg-blue-50/60 border border-blue-100 rounded-xl flex items-center justify-between text-xs">
            <div>
              <span className="font-bold text-blue-900 text-sm">{selectedChildObj.user?.name}</span>
              <p className="text-slate-600 mt-0.5">
                Level: <strong className="capitalize">{selectedChildObj.learning_level}</strong> | 
                Requirements: {selectedChildObj.learning_requirements || 'Standard'}
              </p>
            </div>
            <Badge variant="default">Active Selected Learner</Badge>
          </div>
        )}

        {/* Overview Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-50 text-[#2563EB] rounded-xl flex items-center justify-center font-bold">
              <TrendingUp size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Overall Progress</p>
              <p className="text-2xl font-extrabold text-slate-900">68%</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-teal-50 text-[#14B8A6] rounded-xl flex items-center justify-center font-bold">
              <Award size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Avg Quiz Score</p>
              <p className="text-2xl font-extrabold text-slate-900">82.5%</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center font-bold">
              <Clock size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Time Spent (Week)</p>
              <p className="text-2xl font-extrabold text-slate-900">2.4 hrs</p>
            </div>
          </Card>

          <Card className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center font-bold">
              <Sparkles size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-semibold uppercase">Active Recommendations</p>
              <p className="text-2xl font-extrabold text-slate-900">2 Modules</p>
            </div>
          </Card>
        </div>

        {/* Performance Chart & Recent History */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Topic Performance Overview</CardTitle>
              <CardDescription>Recent quiz scores for {selectedChildObj?.user?.name || 'Selected Child'}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis dataKey="topic" tick={{ fontSize: 12, fill: '#64748B' }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#64748B' }} />
                    <Tooltip cursor={{ fill: '#F1F5F9' }} />
                    <Bar dataKey="score" fill="#2563EB" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-base">AI Recommendation Insights</CardTitle>
              <CardDescription>Transformer + DRL Agent state analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg space-y-1">
                <span className="font-bold text-blue-900">Current Learner State:</span>
                <p className="text-blue-800">Visual retention high. Stable performance in Level 1 Math.</p>
              </div>

              <div className="p-3 bg-teal-50 border border-teal-200 rounded-lg space-y-1">
                <span className="font-bold text-teal-900">PPO Agent Selected Action:</span>
                <p className="text-teal-800">Action 2: Maintain current difficulty level with visual aids.</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
