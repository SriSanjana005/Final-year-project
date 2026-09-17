import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { recommendationService } from '../../services/recommendationService';
import api from '../../services/api';
import { Sparkles, Loader2, Cpu, CheckCircle2, ShieldCheck, Database, Award, AlertCircle } from 'lucide-react';

export function RecommendationMonitoringPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [aiStatus, setAiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        const [recs, statusRes] = await Promise.all([
          recommendationService.getAdminRecommendations(),
          api.get('/recommendations/ai-status').then(r => r.data).catch(() => null)
        ]);
        setRecommendations(recs);
        setAiStatus(statusRes);
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

  const formatStatusBadge = (statusStr) => {
    if (statusStr === 'trained') {
      return <Badge variant="success" className="gap-1"><CheckCircle2 size={12} /> Trained</Badge>;
    } else if (statusStr === 'initialized') {
      return <Badge variant="warning" className="gap-1"><Sparkles size={12} /> Initialized</Badge>;
    }
    return <Badge variant="neutral" className="gap-1"><AlertCircle size={12} /> Unavailable</Badge>;
  };

  const tDetails = aiStatus?.transformer_details || {};
  const ppoDetails = aiStatus?.ppo_details || {};

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="text-blue-600" /> ML Model & Recommendation System Monitoring
          </h1>
          <p className="text-sm text-slate-500">
            Truthful system status audit of <strong>PyTorch Transformer & PPO RL Agent Pipeline</strong>.
          </p>
        </div>

        {/* AI System Status Panel */}
        <div className="bg-slate-900 text-white p-6 rounded-2xl border border-slate-800 space-y-4 shadow-md">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase tracking-wider">
              <Cpu size={18} /> Model Training & Dataset Status Matrix
            </div>
            <Badge variant="success" className="gap-1 bg-teal-500/20 text-teal-300 border-teal-500/30">
              <ShieldCheck size={12} /> Configured Strategy: {aiStatus?.global_configured_strategy || 'AUTO'}
            </Badge>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 font-medium">Transformer Encoder (64-D)</span>
                {formatStatusBadge(tDetails.status)}
              </div>
              <p className="text-xs text-slate-300">
                Samples: <strong>{tDetails.train_samples || 0}</strong> | Acc: <strong>{tDetails.test_accuracy || 'N/A'}</strong>
              </p>
            </div>

            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 font-medium">PPO RL Agent</span>
                {formatStatusBadge(ppoDetails.status)}
              </div>
              <p className="text-xs text-slate-300">
                Timesteps: <strong>{ppoDetails.total_timesteps || 0}</strong> | Reward: <strong>{ppoDetails.mean_reward || 'N/A'}</strong>
              </p>
            </div>

            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700 space-y-2">
              <span className="text-slate-400 font-medium flex items-center gap-1">
                <Database size={14} className="text-amber-400" /> Database Interactions
              </span>
              <p className="text-base font-extrabold text-amber-400">
                {aiStatus?.interaction_count || 0} Records Recorded
              </p>
            </div>

            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700 space-y-2">
              <span className="text-slate-400 font-medium flex items-center gap-1">
                <Award size={14} className="text-blue-400" /> Cold-Start Protocol
              </span>
              <p className="text-xs text-slate-300">
                Threshold: <strong>{aiStatus?.min_required_interactions || 3} Interactions</strong>
                <br />
                Fallback: <strong>Rule-Based Baseline</strong>
              </p>
            </div>
          </div>
        </div>

        {/* Recommendation Stream */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Generated Recommendation Audit Log Stream</CardTitle>
            <CardDescription>
              Chronological log stream of recommendations generated across Transformer+PPO and Rule-Based Fallback.
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
                      <th className="pb-3 px-2">Engine Strategy</th>
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
                        <td className="py-3 px-2 font-semibold">
                          <Badge variant={rec.recommendation_type === 'transformer_ppo' ? 'success' : 'default'}>
                            {rec.recommendation_type === 'transformer_ppo' ? 'Transformer + PPO' : 'Rule-Based Baseline'}
                          </Badge>
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
