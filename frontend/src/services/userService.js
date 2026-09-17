import api from './api';

export const userService = {
  // Common
  getMe: async () => {
    const res = await api.get('/users/me');
    return res.data;
  },

  // Child Profile
  getChildProfile: async () => {
    const res = await api.get('/children/me');
    return res.data;
  },

  // Parent Profile & Children
  getParentProfile: async () => {
    const res = await api.get('/parents/me');
    return res.data;
  },

  getParentChildren: async () => {
    const res = await api.get('/parents/me/children');
    return res.data;
  },

  // Admin Methods
  getUsers: async () => {
    const res = await api.get('/users');
    return res.data;
  },

  createUser: async (userData) => {
    const res = await api.post('/users', userData);
    return res.data;
  },

  deleteUser: async (userId) => {
    const res = await api.delete(`/users/${userId}`);
    return res.data;
  },

  getChildren: async () => {
    const res = await api.get('/children');
    return res.data;
  },

  getParents: async () => {
    const res = await api.get('/parents');
    return res.data;
  },

  getMappings: async () => {
    const res = await api.get('/parent-child');
    return res.data;
  },

  createMapping: async (parentId, childId, relationshipType = "Parent") => {
    const res = await api.post('/parent-child', {
      parent_id: parseInt(parentId),
      child_id: parseInt(childId),
      relationship_type: relationshipType
    });
    return res.data;
  },

  deleteMapping: async (mappingId) => {
    const res = await api.delete(`/parent-child/${mappingId}`);
    return res.data;
  },

  getAdminMetrics: async () => {
    const res = await api.get('/admin/metrics');
    return res.data;
  }
};
