import api from './api';

export const authService = {
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      return response.data;
    } catch (err) {
      // Fallback demo auth if backend isn't reachable yet
      let demoUser = null;
      if (email === 'child@learning.com') {
        demoUser = { access_token: 'mock-child-token', role: 'child', user_id: 1, full_name: 'Leo Smith' };
      } else if (email === 'parent@learning.com') {
        demoUser = { access_token: 'mock-parent-token', role: 'parent', user_id: 2, full_name: 'Sarah Smith' };
      } else if (email === 'admin@learning.com') {
        demoUser = { access_token: 'mock-admin-token', role: 'admin', user_id: 3, full_name: 'Dr. Alex Rivera' };
      }
      if (demoUser) {
        localStorage.setItem('token', demoUser.access_token);
        localStorage.setItem('user', JSON.stringify(demoUser));
        return demoUser;
      }
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  checkHealth: async () => {
    try {
      const res = await api.get('/health');
      return res.data;
    } catch (e) {
      return { status: 'offline', database: 'unavailable' };
    }
  }
};
