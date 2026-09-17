import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { quizService } from '../../services/quizService';
import { contentService } from '../../services/contentService';
import { HelpCircle, Plus, Edit2, Trash2, Eye, X, Check, AlertCircle } from 'lucide-react';

export function QuizManagementPage() {
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingQuiz, setEditingQuiz] = useState(null);

  // Form State
  const [title, setTitle] = useState("");
  const [topicId, setTopicId] = useState("");
  const [difficulty, setDifficulty] = useState("easy");
  const [description, setDescription] = useState("");
  const [isPublished, setIsPublished] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [qData, tData] = await Promise.all([
        quizService.getQuizzes(),
        contentService.getTopics(false)
      ]);
      setQuizzes(qData);
      setTopics(tData);
    } catch (err) {
      console.error("Failed to load quizzes:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openAddModal = () => {
    setEditingQuiz(null);
    setTitle("");
    setTopicId(topics.length > 0 ? topics[0].id.toString() : "");
    setDifficulty("easy");
    setDescription("");
    setIsPublished(false);
    setIsModalOpen(true);
  };

  const openEditModal = (q) => {
    setEditingQuiz(q);
    setTitle(q.title);
    setTopicId(q.topic_id.toString());
    setDifficulty(q.difficulty);
    setDescription(q.description || "");
    setIsPublished(q.is_published);
    setIsModalOpen(true);
  };

  const handleSaveQuiz = async (e) => {
    e.preventDefault();
    if (!title.trim() || !topicId) {
      alert("Title and Topic are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        title,
        topic_id: parseInt(topicId),
        difficulty,
        description,
        is_published: isPublished
      };

      if (editingQuiz) {
        await quizService.updateQuiz(editingQuiz.id, payload);
      } else {
        await quizService.createQuiz(payload);
      }

      setIsModalOpen(false);
      loadData();
    } catch (err) {
      alert("Failed to save quiz: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTogglePublish = async (quiz) => {
    try {
      await quizService.togglePublishQuiz(quiz.id, !quiz.is_published);
      loadData();
    } catch (err) {
      alert("Failed to toggle publish status");
    }
  };

  const handleDeleteQuiz = async (quizId) => {
    if (!window.confirm("Are you sure you want to delete this quiz assessment? Questions and attempt logs will be removed.")) {
      return;
    }
    try {
      await quizService.deleteQuiz(quizId);
      loadData();
    } catch (err) {
      alert("Failed to delete quiz");
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
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <HelpCircle className="text-[#2563EB]" /> Quiz Management
            </h1>
            <p className="text-sm text-slate-500">Configure quiz assessments, difficulty levels, and published status.</p>
          </div>
          <Button variant="primary" className="gap-2 text-xs" onClick={openAddModal}>
            <Plus size={16} /> Create New Quiz
          </Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Configured Quizzes ({quizzes.length})</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading quiz assessments...</div>
            ) : quizzes.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">No quizzes configured yet. Click "Create New Quiz" to get started.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">Quiz Title</th>
                      <th className="pb-3 px-2">Topic & Subject</th>
                      <th className="pb-3 px-2">Difficulty</th>
                      <th className="pb-3 px-2">Questions</th>
                      <th className="pb-3 px-2">Published Status</th>
                      <th className="pb-3 px-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {quizzes.map((q) => (
                      <tr key={q.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-slate-800">{q.title}</td>
                        <td className="py-3 px-2">
                          <span className="font-medium text-slate-700 block">{q.topic?.name || 'N/A'}</span>
                          <span className="text-[10px] text-slate-400">{q.topic?.subject}</span>
                        </td>
                        <td className="py-3 px-2">{getDifficultyBadge(q.difficulty)}</td>
                        <td className="py-3 px-2 font-semibold text-slate-600">{q.question_count} Questions</td>
                        <td className="py-3 px-2">
                          <button 
                            onClick={() => handleTogglePublish(q)}
                            className="cursor-pointer inline-flex items-center gap-1"
                            title="Click to toggle publish status"
                          >
                            <Badge variant={q.is_published ? "success" : "neutral"}>
                              {q.is_published ? "Published" : "Draft / Unpublished"}
                            </Badge>
                          </button>
                        </td>
                        <td className="py-3 px-2 text-right space-x-1.5">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="h-8 px-2 text-xs"
                            onClick={() => navigate(`/admin/questions?quiz_id=${q.id}`)}
                          >
                            Questions ({q.question_count})
                          </Button>
                          <Button variant="ghost" size="sm" className="h-8 px-2" onClick={() => openEditModal(q)}>
                            <Edit2 size={14} />
                          </Button>
                          <Button variant="danger" size="sm" className="h-8 px-2" onClick={() => handleDeleteQuiz(q.id)}>
                            <Trash2 size={14} />
                          </Button>
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

      {/* Add / Edit Quiz Form Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingQuiz ? "Edit Quiz Assessment" : "Create New Quiz Assessment"}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSaveQuiz} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Quiz Title</label>
                <input 
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Basic Addition Quiz"
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Topic</label>
                <select 
                  value={topicId}
                  onChange={(e) => setTopicId(e.target.value)}
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">-- Choose Topic --</option>
                  {topics.map(t => (
                    <option key={t.id} value={t.id}>{t.subject} - {t.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Difficulty</label>
                <select 
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="easy">Easy (Level 1)</option>
                  <option value="medium">Medium (Level 2)</option>
                  <option value="hard">Hard (Level 3)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
                <textarea 
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of quiz assessment..."
                  className="w-full p-3 border border-slate-300 rounded-lg text-xs h-20 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <input 
                  type="checkbox"
                  id="isQuizPublishedCheck"
                  checked={isPublished}
                  onChange={(e) => setIsPublished(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="isQuizPublishedCheck" className="text-xs font-semibold text-slate-800">
                  Publish quiz (Makes quiz visible to children)
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save Quiz"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
