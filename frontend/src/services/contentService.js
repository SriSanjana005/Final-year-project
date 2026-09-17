import api from './api';

export const contentService = {
  // --- TOPIC SERVICES ---
  getTopics: async (activeOnly = false) => {
    const res = await api.get(`/topics?active_only=${activeOnly}`);
    return res.data;
  },

  getActiveTopics: async () => {
    const res = await api.get('/topics/active');
    return res.data;
  },

  getTopicById: async (topicId) => {
    const res = await api.get(`/topics/${topicId}`);
    return res.data;
  },

  createTopic: async (topicData) => {
    const res = await api.post('/topics', topicData);
    return res.data;
  },

  updateTopic: async (topicId, topicData) => {
    const res = await api.put(`/topics/${topicId}`, topicData);
    return res.data;
  },

  deleteTopic: async (topicId) => {
    const res = await api.delete(`/topics/${topicId}`);
    return res.data;
  },

  // --- CONTENT SERVICES ---
  getContentList: async (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.topic_id) searchParams.append('topic_id', params.topic_id);
    if (params.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params.content_type) searchParams.append('content_type', params.content_type);
    if (params.is_published !== undefined && params.is_published !== '') {
      searchParams.append('is_published', params.is_published);
    }
    if (params.search) searchParams.append('search', params.search);

    const queryString = searchParams.toString();
    const url = `/content${queryString ? `?${queryString}` : ''}`;
    const res = await api.get(url);
    return res.data;
  },

  getPublishedContent: async (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.topic_id) searchParams.append('topic_id', params.topic_id);
    if (params.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params.content_type) searchParams.append('content_type', params.content_type);

    const queryString = searchParams.toString();
    const url = `/content/published${queryString ? `?${queryString}` : ''}`;
    const res = await api.get(url);
    return res.data;
  },

  getContentById: async (contentId) => {
    const res = await api.get(`/content/${contentId}`);
    return res.data;
  },

  createContent: async (contentData) => {
    const res = await api.post('/content', contentData);
    return res.data;
  },

  updateContent: async (contentId, contentData) => {
    const res = await api.put(`/content/${contentId}`, contentData);
    return res.data;
  },

  togglePublishContent: async (contentId, isPublished) => {
    const res = await api.patch(`/content/${contentId}/publish`, { is_published: isPublished });
    return res.data;
  },

  deleteContent: async (contentId) => {
    const res = await api.delete(`/content/${contentId}`);
    return res.data;
  }
};
