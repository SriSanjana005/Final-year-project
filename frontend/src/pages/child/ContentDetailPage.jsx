import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { contentService } from '../../services/contentService';
import { recommendationService } from '../../services/recommendationService';
import { ArrowLeft, CheckCircle, Clock, BookOpen, Sparkles } from 'lucide-react';

export function ContentDetailPage() {
  const { contentId } = useParams();
  const navigate = useNavigate();
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        const data = await contentService.getContentById(contentId);
        setContent(data);
      } catch (err) {
        setErrorMsg("Unable to access this learning content module.");
      } finally {
        setLoading(false);
      }
    };
    fetchContent();
  }, [contentId]);

  const handleMarkCompleted = async () => {
    setCompleted(true);
    try {
      const currentRec = await recommendationService.getCurrentRecommendation();
      if (currentRec && currentRec.content_id === parseInt(contentId)) {
        await recommendationService.markCompleted(currentRec.id);
      }
    } catch (err) {
      console.log("Completed content update log.");
    }
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        <button 
          onClick={() => navigate('/child/learning')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-blue-600 transition-colors cursor-pointer"
        >
          <ArrowLeft size={16} /> Back to Learning Library
        </button>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading lesson material...</div>
        ) : errorMsg || !content ? (
          <Card className="p-8 text-center text-red-600 space-y-3">
            <h3 className="font-bold text-base">Content Not Available</h3>
            <p className="text-xs text-slate-500">{errorMsg || "This item may be unpublished or deleted."}</p>
            <Button variant="outline" size="sm" onClick={() => navigate('/child/learning')}>
              Return to Catalog
            </Button>
          </Card>
        ) : (
          <Card className="p-6 md:p-8 shadow-md border border-slate-200 space-y-6">
            {/* Header info */}
            <div className="border-b border-slate-100 pb-4 space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="default">{content.topic?.subject || 'General'}</Badge>
                <Badge variant="success" className="capitalize">{content.difficulty} Difficulty</Badge>
                <Badge variant="neutral" className="capitalize">{content.content_type}</Badge>
                <span className="text-xs text-slate-400 flex items-center gap-1 ml-auto">
                  <Clock size={14} /> {content.estimated_duration} mins
                </span>
              </div>

              <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight pt-1">
                {content.title}
              </h1>
              {content.description && (
                <p className="text-sm text-slate-500">{content.description}</p>
              )}
            </div>

            {/* Distraction-Free Learning Body Area */}
            <div className="p-6 md:p-8 bg-slate-50 rounded-2xl border border-slate-200 text-slate-900 text-base md:text-lg leading-relaxed space-y-4">
              <div className="whitespace-pre-line font-sans">
                {content.content_body}
              </div>
            </div>

            {/* Completion Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-slate-100">
              <Button variant="outline" size="md" onClick={() => navigate('/child/learning')}>
                Back to Topics
              </Button>

              <Button 
                variant={completed ? "success" : "primary"}
                size="lg" 
                className="gap-2 w-full sm:w-auto font-semibold"
                onClick={handleMarkCompleted}
              >
                {completed ? (
                  <>
                    <CheckCircle size={18} /> Completed!
                  </>
                ) : (
                  <>
                    <Sparkles size={18} /> Mark as Completed
                  </>
                )}
              </Button>
            </div>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}

