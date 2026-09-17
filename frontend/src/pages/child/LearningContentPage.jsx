import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { contentService } from '../../services/contentService';
import { BookOpen, Clock, Play, Sparkles, CheckCircle2 } from 'lucide-react';

export function LearningContentPage() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [publishedContent, setPublishedContent] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [tData, cData] = await Promise.all([
          contentService.getActiveTopics(),
          contentService.getPublishedContent()
        ]);
        setTopics(tData);
        setPublishedContent(cData);
      } catch (err) {
        console.error("Failed to load published learning content:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredContent = selectedTopicId === "all" 
    ? publishedContent 
    : publishedContent.filter(c => c.topic_id.toString() === selectedTopicId);

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
            <BookOpen className="text-[#2563EB]" /> Educational Learning Library
          </h1>
          <p className="text-sm text-slate-500">Explore approved learning modules designed for visual clarity.</p>
        </div>

        {/* Topic Filter Tabs */}
        <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
          <button
            onClick={() => setSelectedTopicId("all")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
              selectedTopicId === "all"
                ? 'bg-[#2563EB] text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            All Topics ({publishedContent.length})
          </button>

          {topics.map((t) => (
            <button
              key={t.id}
              onClick={() => setSelectedTopicId(t.id.toString())}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                selectedTopicId === t.id.toString()
                  ? 'bg-[#2563EB] text-white shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {t.subject} - {t.name}
            </button>
          ))}
        </div>

        {/* Content Items Grid */}
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading learning modules...</div>
        ) : filteredContent.length === 0 ? (
          <Card className="p-12 text-center text-slate-500 space-y-2">
            <BookOpen size={36} className="mx-auto text-slate-300" />
            <h3 className="font-bold text-slate-800 text-base">No learning content available yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No published learning content items match this topic filter. Please select another topic or check back later!
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item) => (
              <Card key={item.id} className="border border-slate-200 hover:border-blue-300 transition-all flex flex-col justify-between">
                <CardHeader>
                  <div className="flex justify-between items-center mb-1">
                    <Badge variant="default">{item.topic?.subject || 'General'}</Badge>
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Clock size={12} /> {item.estimated_duration} mins
                    </span>
                  </div>
                  <CardTitle className="text-base pt-1">{item.title}</CardTitle>
                  <CardDescription className="line-clamp-2">{item.description || item.content_body}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    {getDifficultyBadge(item.difficulty)}
                    <Badge variant="neutral" className="capitalize">{item.content_type}</Badge>
                  </div>

                  <Button 
                    variant="primary" 
                    size="md" 
                    className="w-full gap-2 text-xs font-semibold"
                    onClick={() => navigate(`/child/learning/${item.id}`)}
                  >
                    <Play size={16} /> Start Learning
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
