import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { contentService } from '../../services/contentService';
import { FileText, Plus, Search, Filter, Edit2, Trash2, Eye, CheckCircle, XCircle, X, Sparkles } from 'lucide-react';

export function ContentManagementPage() {
  const [contentList, setContentList] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  // Search & Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [filterTopicId, setFilterTopicId] = useState("");
  const [filterDifficulty, setFilterDifficulty] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  // Modals
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [previewContent, setPreviewContent] = useState(null);

  // Form State
  const [title, setTitle] = useState("");
  const [topicId, setTopicId] = useState("");
  const [contentType, setContentType] = useState("lesson");
  const [difficulty, setDifficulty] = useState("easy");
  const [estimatedDuration, setEstimatedDuration] = useState(10);
  const [description, setDescription] = useState("");
  const [contentBody, setContentBody] = useState("");
  const [isPublished, setIsPublished] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cData, tData] = await Promise.all([
        contentService.getContentList({
          search: searchTerm,
          topic_id: filterTopicId,
          difficulty: filterDifficulty,
          content_type: filterType,
          is_published: filterStatus
        }),
        contentService.getTopics(false)
      ]);
      setContentList(cData);
      setTopics(tData);
    } catch (err) {
      console.error("Failed to load content list:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchTerm, filterTopicId, filterDifficulty, filterType, filterStatus]);

  const openAddModal = () => {
    setEditingContent(null);
    setTitle("");
    setTopicId(topics.length > 0 ? topics[0].id.toString() : "");
    setContentType("lesson");
    setDifficulty("easy");
    setEstimatedDuration(10);
    setDescription("");
    setContentBody("");
    setIsPublished(false);
    setIsFormModalOpen(true);
  };

  const openEditModal = (c) => {
    setEditingContent(c);
    setTitle(c.title);
    setTopicId(c.topic_id.toString());
    setContentType(c.content_type);
    setDifficulty(c.difficulty);
    setEstimatedDuration(c.estimated_duration);
    setDescription(c.description || "");
    setContentBody(c.content_body);
    setIsPublished(c.is_published);
    setIsFormModalOpen(true);
  };

  const handleSaveContent = async (e) => {
    e.preventDefault();
    if (!title.trim() || !topicId || !contentBody.trim()) {
      alert("Title, Topic, and Content Body are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        title,
        topic_id: parseInt(topicId),
        content_type: contentType,
        difficulty,
        estimated_duration: parseInt(estimatedDuration),
        description,
        content_body: contentBody,
        is_published: isPublished
      };

      if (editingContent) {
        await contentService.updateContent(editingContent.id, payload);
      } else {
        await contentService.createContent(payload);
      }

      setIsFormModalOpen(false);
      loadData();
    } catch (err) {
      alert("Failed to save content: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTogglePublish = async (item) => {
    try {
      await contentService.togglePublishContent(item.id, !item.is_published);
      loadData();
    } catch (err) {
      alert("Failed to toggle publish status");
    }
  };

  const handleDeleteContent = async (id) => {
    if (!window.confirm("Are you sure you want to delete this learning content item?")) {
      return;
    }
    try {
      await contentService.deleteContent(id);
      loadData();
    } catch (err) {
      alert("Failed to delete content");
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
              <FileText className="text-[#2563EB]" /> Educational Content Library
            </h1>
            <p className="text-sm text-slate-500">Admin-approved learning material for DRL content pool.</p>
          </div>
          <Button variant="primary" className="gap-2 text-xs" onClick={openAddModal}>
            <Plus size={16} /> Create Learning Content
          </Button>
        </div>

        {/* Search & Filter Toolbar */}
        <Card className="p-4 bg-slate-50/50 border border-slate-200 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
            {/* Search Input */}
            <div className="relative md:col-span-2">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Search size={14} />
              </div>
              <input 
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by content title..."
                className="w-full h-9 pl-8 pr-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Topic Filter */}
            <div>
              <select 
                value={filterTopicId}
                onChange={(e) => setFilterTopicId(e.target.value)}
                className="w-full h-9 px-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Topics</option>
                {topics.map(t => (
                  <option key={t.id} value={t.id}>{t.subject} - {t.name}</option>
                ))}
              </select>
            </div>

            {/* Difficulty Filter */}
            <div>
              <select 
                value={filterDifficulty}
                onChange={(e) => setFilterDifficulty(e.target.value)}
                className="w-full h-9 px-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            {/* Published Status Filter */}
            <div>
              <select 
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full h-9 px-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="true">Published Only</option>
                <option value="false">Unpublished Only</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Content Table */}
        <Card>
          <CardHeader><CardTitle className="text-base">Content Catalog Items ({contentList.length})</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading educational content...</div>
            ) : contentList.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">No learning content found matching your filters.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">Title</th>
                      <th className="pb-3 px-2">Topic & Subject</th>
                      <th className="pb-3 px-2">Type</th>
                      <th className="pb-3 px-2">Difficulty</th>
                      <th className="pb-3 px-2">Duration</th>
                      <th className="pb-3 px-2">Published Status</th>
                      <th className="pb-3 px-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {contentList.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-slate-800">{item.title}</td>
                        <td className="py-3 px-2">
                          <span className="font-medium text-slate-700 block">{item.topic?.name || 'N/A'}</span>
                          <span className="text-[10px] text-slate-400">{item.topic?.subject}</span>
                        </td>
                        <td className="py-3 px-2 capitalize font-semibold text-slate-600">{item.content_type}</td>
                        <td className="py-3 px-2">{getDifficultyBadge(item.difficulty)}</td>
                        <td className="py-3 px-2 text-slate-600">{item.estimated_duration} mins</td>
                        <td className="py-3 px-2">
                          <button 
                            onClick={() => handleTogglePublish(item)}
                            className="cursor-pointer inline-flex items-center gap-1"
                            title="Click to toggle publish status"
                          >
                            <Badge variant={item.is_published ? "success" : "neutral"}>
                              {item.is_published ? "Published" : "Draft / Unpublished"}
                            </Badge>
                          </button>
                        </td>
                        <td className="py-3 px-2 text-right space-x-1.5">
                          <Button variant="ghost" size="sm" className="h-8 px-2" title="Preview" onClick={() => { setPreviewContent(item); setIsPreviewModalOpen(true); }}>
                            <Eye size={14} />
                          </Button>
                          <Button variant="outline" size="sm" className="h-8 px-2" onClick={() => openEditModal(item)}>
                            <Edit2 size={14} />
                          </Button>
                          <Button variant="danger" size="sm" className="h-8 px-2" onClick={() => handleDeleteContent(item.id)}>
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

      {/* Form Modal (Add / Edit) */}
      {isFormModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingContent ? "Edit Educational Content" : "Create Approved Learning Content"}
              </h3>
              <button onClick={() => setIsFormModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSaveContent} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Content Title</label>
                <input 
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Introduction to Addition with Visual Blocks"
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Content Type</label>
                  <select 
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                    className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="lesson">Lesson</option>
                    <option value="video">Video</option>
                    <option value="practice">Practice</option>
                    <option value="activity">Activity</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Difficulty Level</label>
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
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Estimated Duration (Mins)</label>
                  <input 
                    type="number"
                    value={estimatedDuration}
                    onChange={(e) => setEstimatedDuration(e.target.value)}
                    min="1"
                    className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description / Summary</label>
                <input 
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Short lesson summary..."
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Learning Material Body</label>
                <textarea 
                  value={contentBody}
                  onChange={(e) => setContentBody(e.target.value)}
                  placeholder="Enter the main educational content body text..."
                  className="w-full p-3 border border-slate-300 rounded-lg text-xs h-32 focus:ring-2 focus:ring-blue-500 font-sans leading-relaxed"
                  required
                />
              </div>

              <div className="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <input 
                  type="checkbox"
                  id="isPublishedCheck"
                  checked={isPublished}
                  onChange={(e) => setIsPublished(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="isPublishedCheck" className="text-xs font-semibold text-slate-800">
                  Publish immediately (Makes content visible to child learners)
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsFormModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save Content"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {isPreviewModalOpen && previewContent && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <div>
                <Badge variant="default">{previewContent.topic?.subject} - {previewContent.topic?.name}</Badge>
                <h3 className="font-bold text-slate-900 text-lg mt-1">{previewContent.title}</h3>
              </div>
              <button onClick={() => setIsPreviewModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
              <div className="flex gap-2">
                <Badge variant="success" className="capitalize">{previewContent.difficulty} Difficulty</Badge>
                <Badge variant="neutral" className="capitalize">{previewContent.content_type}</Badge>
                <Badge variant="neutral">{previewContent.estimated_duration} mins</Badge>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-mono bg-white p-3 border border-slate-200 rounded-lg">
                {previewContent.content_body}
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="outline" size="sm" onClick={() => setIsPreviewModalOpen(false)}>Close Preview</Button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
