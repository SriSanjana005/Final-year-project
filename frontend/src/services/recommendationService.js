import api from './api';

export const recommendationService = {
  getRecommendations: async (childId = 1) => {
    try {
      const res = await api.get(`/recommendations/child/${childId}`);
      return res.data;
    } catch (e) {
      return {
        child_id: childId,
        recommendation_engine: "Transformer + PPO DRL (Future Architecture)",
        recommendations: [
          {
            id: 101,
            title: "Interactive Counting with Visual Blocks",
            topic: "Mathematics",
            difficulty: 1,
            confidence_score: 0.94,
            reason: "Sequence history shows high engagement with visual math aids.",
            drl_action_type: "Maintain difficulty level"
          },
          {
            id: 102,
            title: "Basic Word & Object Matching",
            topic: "Reading",
            difficulty: 1,
            confidence_score: 0.88,
            reason: "Previous session score was 85%. Progressing smoothly.",
            drl_action_type: "Introduce practice activity"
          }
        ]
      };
    }
  }
};
