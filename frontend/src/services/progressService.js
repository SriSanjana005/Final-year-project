import api from './api';

export const progressService = {
  getChildProgress: async (childId) => {
    const res = await api.get(`/progress/child/${childId}`);
    return res.data;
  },

  getChildHistory: async (childId) => {
    const res = await api.get(`/history/child/${childId}`);
    return res.data;
  }
};
