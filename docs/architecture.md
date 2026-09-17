# System Architecture

## Overview
The **Transformer-Based Personalized Learning Recommendation System for Children with Special Needs** is a full-stack, AI-driven educational platform designed to deliver personalized content recommendations to young learners.

The system combines:
1. **Frontend**: React 18, Vite, JavaScript, Tailwind CSS, shadcn/ui, Recharts.
2. **Backend**: Python 3.11, FastAPI, SQLAlchemy ORM, MySQL / SQLite database.
3. **Machine Learning Pipeline**:
   - **Transformer Encoder**: 64-dimensional learner state extraction from historical sequence data.
   - **PPO Reinforcement Learning Agent**: Stable-Baselines3 Gymnasium agent selecting high-level action types (0–4).
   - **Content Selection Engine**: Rules-based mapping from RL action types to published admin educational modules.

---

## High-Level Component Interaction

```
+-----------------------------------------------------------------------+
|                            USER INTERFACE                             |
|    Child Dashboard  |  Parent Progress Portal  |  Admin Control Panel   |
+-----------------------------------------------------------------------+
                                  |
                           REST API / JWT
                                  v
+-----------------------------------------------------------------------+
|                           FASTAPI BACKEND                             |
|  Auth / RBAC  |  Quizzes  |  LearningHistory  |  RecommendationService|
+-----------------------------------------------------------------------+
                                  |
                                  +-----------------------+
                                  v                       v
                      +-----------------------+ +--------------------+
                      |     MYSQL DATABASE    | |    AI SUBSYSTEM    |
                      |  Users, Content,      | | Transformer (64D)  |
                      |  Attempts, History    | | PPO Agent (68D)    |
                      +-----------------------+ +--------------------+
```

---

## Role-Based Access Control (RBAC)
- **Child (`child`)**: Access to assigned learning modules, published quizzes, self progress, active recommendations.
- **Parent (`parent`)**: Access to linked children progress, performance summaries, and recommendations.
- **Admin (`admin`)**: Access to curriculum content management, quiz creation, user administration, system evaluation metrics.
