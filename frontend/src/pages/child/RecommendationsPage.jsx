import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { recommendationService } from '../../services/recommendationService';
import { Sparkles, Play, RefreshCw, Loader2, Info } from 'lucide-react';

export function RecommendationsPage() {
  const navigate = useNavigate();
  const [currentRec, setCurrentRec] = useState(null);
  const [historyRecs, setHistoryRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const current = await recommendationService.getCurrentRecommendation();
      const all = await recommendationService.getRecommendations();
      setCurrentRec(current);
      setHistoryRecs(all);
    } catch (err) {
      console.error("Failed to load recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  const handleGenerateNew = async () => {
    try {
      setGenerating(true);
      await recommendationService.generateRecommendation();
      await loadRecommendations();
    } catch (err) {
      alert("Failed to generate recommendation: " + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleStartLearning = async (rec) => {
    try {
      if (rec.status === 'recommended') {
        await recommendationService.markViewed(rec.id);
      }
      navigate(`/child/learning/${rec.content_id}`);
    } catch (err) {
      navigate(`/child/learning/${rec.content_id}`);
    }
  };

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
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="text-blue-600" /> Recommended For You
            </h1>
            <p className="text-sm text-slate-500">
              Personalized learning modules suggested by the <strong>Rule-Based Recommendation Baseline</strong>.
            </p>
          </div>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleGenerateNew} 
            disabled={generating}
            className="gap-2 text-xs font-semibold"
          >
            <RefreshCw size={14} className={generating ? "animate-spin" : ""} />
            Refresh Recommendation
          </Button>
        </div>

        {/* Baseline System Rationale Banner */}
        <div className="bg-slate-900 text-white p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase tracking-wider">
            <Info size={16} /> Rule-Based Baseline Engine Rationale
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            This recommendation baseline analyzes your recent quiz scores ($N=3$ window). Scores under 50% trigger easy review modules, scores between 50% and 80% maintain current difficulty, and scores above 80% recommend higher difficulty modules.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="animate-spin text-blue-600" size={32} />
          </div>
        ) : (
          <div className="space-y-8">
            {/* Top / Current Active Recommendation */}
            {currentRec && (
              <Card className="border-2 border-blue-500 bg-blue-50/20 shadow-md">
                <CardHeader>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
                      ★ Primary Recommended Module
                    </span>
                    {getDifficultyBadge(currentRec.difficulty)}
                  </div>
                  <CardTitle className="text-xl text-slate-900">{currentRec.content_title}</CardTitle>
                  <CardDescription className="text-xs font-semibold text-slate-600">
                    Topic: {currentRec.topic_name || 'General'} | Engine: <span className="capitalize">{currentRec.recommendation_type.replace('_', ' ')} Baseline</span>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-white border border-blue-100 rounded-xl text-xs space-y-1 text-slate-700 shadow-2xs">
                    <span className="font-bold text-slate-900">Recommendation Reason:</span>
                    <p className="text-slate-600">{currentRec.reason}</p>
                  </div>

                  <Button 
                    variant="primary" 
                    size="lg" 
                    className="w-full gap-2 font-bold shadow-xs"
                    onClick={() => handleStartLearning(currentRec)}
                  >
                    <Play size={18} /> Start Learning
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Recommendation History List */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-slate-900">Recent Recommendation History</h3>
              {historyRecs.length === 0 ? (
                <p className="text-xs text-slate-500">No recommendation history recorded.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {historyRecs.map((rec) => (
                    <Card key={rec.id} className="border border-slate-200">
                      <CardHeader className="p-4 pb-2">
                        <div className="flex justify-between items-center mb-1">
                          <Badge variant="default">{rec.topic_name || 'General'}</Badge>
                          <Badge variant={rec.status === 'completed' ? 'success' : rec.status === 'viewed' ? 'warning' : 'default'}>
                            {rec.status}
                          </Badge>
                        </div>
                        <CardTitle className="text-base">{rec.content_title}</CardTitle>
                      </CardHeader>
                      <CardContent className="p-4 pt-0 space-y-3">
                        <p className="text-xs text-slate-600 line-clamp-2">{rec.reason}</p>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full text-xs font-semibold"
                          onClick={() => handleStartLearning(rec)}
                        >
                          View Content
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

