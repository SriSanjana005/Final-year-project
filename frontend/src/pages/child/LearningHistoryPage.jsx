import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { useAuth } from '../../context/AuthContext';
import { progressService } from '../../services/progressService';
import { History, Loader2, Calendar, Clock, Award } from 'lucide-react';

export function LearningHistoryPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const childId = user?.child_profile_id || user?.id;
        if (childId) {
          const data = await progressService.getChildHistory(childId);
          setHistory(data);
        }
      } catch (err) {
        console.error("Failed to load history:", err);
        setError("Failed to load interaction sequence log.");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [user]);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Learning History</h1>
          <p className="text-sm text-slate-500">Recorded sequential interaction logs used by the Transformer model.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <History size={18} className="text-blue-600" />
              Interaction Sequence Log
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="animate-spin text-blue-600" size={32} />
              </div>
            ) : error ? (
              <div className="text-center py-8 text-red-500 text-sm">{error}</div>
            ) : history.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">
                No learning history recorded yet. Complete quizzes or view lessons to generate activity logs.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">Timestamp</th>
                      <th className="pb-3 px-2">Activity Type</th>
                      <th className="pb-3 px-2">Topic</th>
                      <th className="pb-3 px-2">Difficulty</th>
                      <th className="pb-3 px-2">Duration</th>
                      <th className="pb-3 px-2">Score</th>
                      <th className="pb-3 px-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {history.map((row) => (
                      <tr key={row.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 text-slate-500">
                          {new Date(row.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-2 font-semibold text-slate-800 capitalize">
                          {row.activity_type}
                        </td>
                        <td className="py-3 px-2 text-slate-700 font-medium">
                          {row.topic_name || `Topic #${row.topic_id}`}
                        </td>
                        <td className="py-3 px-2 text-slate-600 capitalize">
                          {row.difficulty || 'beginner'}
                        </td>
                        <td className="py-3 px-2 text-slate-600">
                          {row.time_spent ? `${Math.round(row.time_spent / 60)} mins` : 'N/A'}
                        </td>
                        <td className="py-3 px-2 font-bold text-teal-600">
                          {row.score !== null && row.score !== undefined ? `${Math.round(row.score)}%` : 'N/A'}
                        </td>
                        <td className="py-3 px-2">
                          <Badge variant={row.completion_status === 'completed' ? 'success' : 'default'}>
                            {row.completion_status}
                          </Badge>
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

