import api from './api';

export const recommendationService = {
  getCurrentRecommendation: async (childId = null) => {
    const params = childId ? { child_id: childId } : {};
    const res = await api.get('/recommendations/current', { params });
    return res.data;
  },

  getRecommendations: async (childId = null) => {
    const params = childId ? { child_id: childId } : {};
    const res = await api.get('/recommendations', { params });
    return res.data;
  },

  generateRecommendation: async (childId = null) => {
    const params = childId ? { child_id: childId } : {};
    const res = await api.post('/recommendations/generate', null, { params });
    return res.data;
  },

  markViewed: async (recommendationId) => {
    const res = await api.post(`/recommendations/${recommendationId}/view`);
    return res.data;
  },

  markCompleted: async (recommendationId) => {
    const res = await api.post(`/recommendations/${recommendationId}/complete`);
    return res.data;
  },

  getAdminRecommendations: async () => {
    const res = await api.get('/recommendations/admin/all');
    return res.data;
  }
};
