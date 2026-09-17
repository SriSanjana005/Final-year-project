import api from './api';

export const quizService = {
  // --- ADMIN QUIZ SERVICES ---
  getQuizzes: async () => {
    const res = await api.get('/quizzes');
    return res.data;
  },

  getPublishedQuizzes: async () => {
    const res = await api.get('/quizzes/published');
    return res.data;
  },

  getQuizById: async (quizId) => {
    const res = await api.get(`/quizzes/${quizId}`);
    return res.data;
  },

  createQuiz: async (quizData) => {
    const res = await api.post('/quizzes', quizData);
    return res.data;
  },

  updateQuiz: async (quizId, quizData) => {
    const res = await api.put(`/quizzes/${quizId}`, quizData);
    return res.data;
  },

  togglePublishQuiz: async (quizId, isPublished) => {
    const res = await api.patch(`/quizzes/${quizId}/publish`, { is_published: isPublished });
    return res.data;
  },

  deleteQuiz: async (quizId) => {
    const res = await api.delete(`/quizzes/${quizId}`);
    return res.data;
  },

  // --- ADMIN QUESTION SERVICES ---
  getQuestions: async (quizId) => {
    const res = await api.get(`/quizzes/${quizId}/questions`);
    return res.data;
  },

  createQuestion: async (quizId, questionData) => {
    const res = await api.post(`/quizzes/${quizId}/questions`, questionData);
    return res.data;
  },

  updateQuestion: async (questionId, questionData) => {
    const res = await api.put(`/questions/${questionId}`, questionData);
    return res.data;
  },

  deleteQuestion: async (questionId) => {
    const res = await api.delete(`/questions/${questionId}`);
    return res.data;
  },

  // --- CHILD QUIZ DELIVERY & SUBMISSION ---
  getQuizForAttempt: async (quizId) => {
    const res = await api.get(`/quizzes/${quizId}/attempt`);
    return res.data;
  },

  submitQuiz: async (quizId, submissionData) => {
    const res = await api.post(`/quizzes/${quizId}/submit`, submissionData);
    return res.data;
  }
};
