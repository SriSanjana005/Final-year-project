import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { contentService } from '../../services/contentService';
import { FolderKanban, Plus, Edit2, Trash2, CheckCircle2, XCircle, AlertCircle, X } from 'lucide-react';

export function TopicManagementPage() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTopic, setEditingTopic] = useState(null);
  
  // Form State
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("Mathematics");
  const [description, setDescription] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadTopics = async () => {
    try {
      setLoading(true);
      const data = await contentService.getTopics(false);
      setTopics(data);
    } catch (err) {
      setErrorMsg("Failed to load topics. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTopics();
  }, []);

  const openAddModal = () => {
    setEditingTopic(null);
    setName("");
    setSubject("Mathematics");
    setDescription("");
    setIsActive(true);
    setIsModalOpen(true);
  };

  const openEditModal = (t) => {
    setEditingTopic(t);
    setName(t.name);
    setSubject(t.subject);
    setDescription(t.description || "");
    setIsActive(t.is_active);
    setIsModalOpen(true);
  };

  const handleSaveTopic = async (e) => {
    e.preventDefault();
    if (!name.trim() || !subject.trim()) {
      alert("Name and Subject are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      if (editingTopic) {
        await contentService.updateTopic(editingTopic.id, {
          name, subject, description, is_active: isActive
        });
      } else {
        await contentService.createTopic({
          name, subject, description, is_active: isActive
        });
      }
      setIsModalOpen(false);
      loadTopics();
    } catch (err) {
      alert("Failed to save topic: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleActive = async (topic) => {
    try {
      await contentService.updateTopic(topic.id, { is_active: !topic.is_active });
      loadTopics();
    } catch (err) {
      alert("Failed to update status");
    }
  };

  const handleDeleteTopic = async (topicId) => {
    if (!window.confirm("Are you sure you want to delete this topic? Associated learning content will be removed.")) {
      return;
    }
    try {
      await contentService.deleteTopic(topicId);
      loadTopics();
    } catch (err) {
      alert("Failed to delete topic");
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <FolderKanban className="text-[#2563EB]" /> Topic Management
            </h1>
            <p className="text-sm text-slate-500">Configure educational subjects, topics, and active availability.</p>
          </div>
          <Button variant="primary" className="gap-2 text-xs" onClick={openAddModal}>
            <Plus size={16} /> Add New Topic
          </Button>
        </div>

        {errorMsg && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
            <AlertCircle size={16} /> {errorMsg}
          </div>
        )}

        <Card>
          <CardHeader><CardTitle className="text-base">Educational Topics ({topics.length})</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading topic catalog...</div>
            ) : topics.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">No topics found. Click "Add New Topic" above to get started.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">Subject</th>
                      <th className="pb-3 px-2">Topic Name</th>
                      <th className="pb-3 px-2">Description</th>
                      <th className="pb-3 px-2">Status</th>
                      <th className="pb-3 px-2">Created Date</th>
                      <th className="pb-3 px-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {topics.map((t) => (
                      <tr key={t.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-[#2563EB]">{t.subject}</td>
                        <td className="py-3 px-2 font-semibold text-slate-800">{t.name}</td>
                        <td className="py-3 px-2 text-slate-500 max-w-xs truncate">{t.description || 'N/A'}</td>
                        <td className="py-3 px-2">
                          <button 
                            onClick={() => handleToggleActive(t)}
                            className="cursor-pointer inline-flex items-center gap-1"
                            title="Click to toggle status"
                          >
                            <Badge variant={t.is_active ? "success" : "neutral"}>
                              {t.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </button>
                        </td>
                        <td className="py-3 px-2 text-slate-500">
                          {t.created_at ? new Date(t.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="py-3 px-2 text-right space-x-2">
                          <Button variant="outline" size="sm" className="h-8 px-2 text-xs" onClick={() => openEditModal(t)}>
                            <Edit2 size={14} /> Edit
                          </Button>
                          <Button variant="danger" size="sm" className="h-8 px-2 text-xs" onClick={() => handleDeleteTopic(t.id)}>
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

      {/* Add / Edit Topic Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingTopic ? "Edit Educational Topic" : "Add New Educational Topic"}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSaveTopic} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Subject</label>
                <select 
                  value={subject} 
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Mathematics">Mathematics</option>
                  <option value="English">English</option>
                  <option value="Science">Science</option>
                  <option value="Logic">Logic & Reasoning</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Topic Name</label>
                <input 
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Addition, Vocabulary, Animals"
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
                <textarea 
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of learning focus..."
                  className="w-full p-3 border border-slate-300 rounded-lg text-xs h-20 focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center gap-2">
                <input 
                  type="checkbox"
                  id="isActiveCheck"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="isActiveCheck" className="text-xs font-medium text-slate-700">Active (Visible to students)</label>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save Topic"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
