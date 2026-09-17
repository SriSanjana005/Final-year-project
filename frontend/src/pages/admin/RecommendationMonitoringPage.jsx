import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { recommendationService } from '../../services/recommendationService';
import { Sparkles, Loader2, Calendar, User, BookOpen, Cpu } from 'lucide-react';


export function RecommendationMonitoringPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        const data = await recommendationService.getAdminRecommendations();
        setRecommendations(data);
      } catch (err) {
        console.error("Failed to load admin recommendations:", err);
        setErrorMsg("Failed to load recommendation records.");
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  const getDifficultyBadge = (diff) => {
    switch (diff) {
      case 'easy':
        return <Badge variant="success">Easy</Badge>;
      case 'medium':
        return <Badge variant="warning">Medium</Badge>;
      case 'hard':
        return <Badge variant="danger">Hard</Badge>;
      default:
        return <Badge variant="neutral">{diff}</Badge>;
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="text-blue-600" /> Recommendation Baseline Logs
          </h1>
          <p className="text-sm text-slate-500">
            System audit log of generated <strong>Rule-Based Recommendations</strong> across all learners.
          </p>
        </div>

        <div className="bg-slate-900 text-white p-5 rounded-2xl border border-slate-800 space-y-3 shadow-sm">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase tracking-wider">
            <Cpu size={16} /> PyTorch Transformer Learner Representation Pipeline
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs pt-1">
            <div className="p-3 bg-slate-800 rounded-xl border border-slate-700">
              <span className="text-slate-400 font-medium">Embedding Dimension</span>
              <p className="text-base font-extrabold text-blue-400 mt-0.5">64-D Vector</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-xl border border-slate-700">
              <span className="text-slate-400 font-medium">Sequence Window (N)</span>
              <p className="text-base font-extrabold text-teal-400 mt-0.5">20 Timesteps</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-xl border border-slate-700">
              <span className="text-slate-400 font-medium">Transformer Encoder</span>
              <p className="text-base font-extrabold text-indigo-400 mt-0.5">2 Layers, 4 Heads</p>
            </div>
            <div className="p-3 bg-slate-800 rounded-xl border border-slate-700">
              <span className="text-slate-400 font-medium">Cold-Start Strategy</span>
              <p className="text-base font-extrabold text-amber-400 mt-0.5">Rule-Based Fallback</p>
            </div>
          </div>
        </div>


        <Card>
          <CardHeader>
            <CardTitle className="text-base">Generated Baseline Recommendations</CardTitle>
            <CardDescription>
              Control baseline records for academic evaluation against future Transformer + PPO architecture.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="animate-spin text-blue-600" size={32} />
              </div>
            ) : errorMsg ? (
              <div className="text-center py-8 text-red-500 text-sm">{errorMsg}</div>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">
                No recommendations generated yet in the system.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">Generated Date</th>
                      <th className="pb-3 px-2">Child Learner</th>
                      <th className="pb-3 px-2">Topic</th>
                      <th className="pb-3 px-2">Recommended Content</th>
                      <th className="pb-3 px-2">Target Difficulty</th>
                      <th className="pb-3 px-2">Engine Type</th>
                      <th className="pb-3 px-2">Reason Rationale</th>
                      <th className="pb-3 px-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {recommendations.map((rec) => (
                      <tr key={rec.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 text-slate-500 whitespace-nowrap">
                          {new Date(rec.generated_at).toLocaleString()}
                        </td>
                        <td className="py-3 px-2 font-bold text-slate-900">
                          {rec.child_name || `Child #${rec.child_id}`}
                        </td>
                        <td className="py-3 px-2 font-medium text-slate-700">
                          {rec.topic_name || 'General'}
                        </td>
                        <td className="py-3 px-2 font-semibold text-blue-600">
                          {rec.content_title}
                        </td>
                        <td className="py-3 px-2">
                          {getDifficultyBadge(rec.difficulty)}
                        </td>
                        <td className="py-3 px-2 font-semibold text-slate-700 capitalize">
                          {rec.recommendation_type.replace('_', '-')} Baseline
                        </td>
                        <td className="py-3 px-2 text-slate-600 max-w-xs truncate" title={rec.reason}>
                          {rec.reason}
                        </td>
                        <td className="py-3 px-2">
                          <Badge variant={rec.status === 'completed' ? 'success' : rec.status === 'viewed' ? 'warning' : 'default'}>
                            {rec.status}
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
