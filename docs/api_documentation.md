# API Documentation

## Authentication Endpoints (`/api/auth`)
- `POST /api/auth/login`: Accepts `{ email, password }`, returns JWT Bearer token and user profile details.
- `GET /api/auth/me`: Returns authenticated user profile.

## User & Profile Endpoints
- `GET /api/users/me`: Current user details.
- `GET /api/children/me`: Child profile details for authenticated child.
- `GET /api/parents/me`: Parent profile details for authenticated parent.
- `GET /api/parents/me/children`: List of linked children for authenticated parent.
- `GET /api/admin/metrics`: Admin system user & relationship metrics.

## Curriculum & Content Endpoints (`/api/topics`, `/api/content`)
- `GET /api/topics`: Active learning topics.
- `GET /api/content/published`: Published learning content modules.
- `GET /api/content/{id}`: Detailed view of a single content item.

## Quiz System Endpoints (`/api/quizzes`)
- `GET /api/quizzes/published`: Published quizzes for child attempt.
- `GET /api/quizzes/{id}/attempt`: Delivers quiz attempt payload stripped of correct answers and explanations.
- `POST /api/quizzes/{id}/submit`: Accepts submitted answers, calculates score on backend, stores attempt and answer records, and updates learning history.

## Performance & History Endpoints (`/api/progress`, `/api/history`)
- `GET /api/progress/child/{child_id}`: Summary performance metrics, topic averages, and recent attempts.
- `GET /api/history/child/{child_id}`: Chronological learning activity history records.

## Recommendation Endpoints (`/api/recommendations`)
- `GET /api/recommendations/ai-status`: AI readiness, cold-start status, and selected strategy.
- `GET /api/recommendations/current`: Current active recommendation for child.
- `POST /api/recommendations/generate`: Generates fresh recommendation using active strategy (`AUTO`, `RULE_BASED`, `TRANSFORMER_PPO`).
- `POST /api/recommendations/{id}/view`: Updates recommendation status to `viewed`.
- `POST /api/recommendations/{id}/complete`: Updates recommendation status to `completed`.
- `GET /api/recommendations/admin/evaluation/summary`: Admin experimental evaluation metrics.
