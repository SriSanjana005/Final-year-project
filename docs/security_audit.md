# Security Audit Report

## 1. Authentication & Password Security
- Passwords are hashed using bcrypt with salt via `app.core.security`. Plaintext passwords are never stored or returned in API responses.
- JWT access tokens rely on `HS256` secret signature with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).

## 2. Server-Side Role & Authorization Enforcement
- Authorization checks (`require_role(["admin"])`, `verify_child_access`) are enforced server-side on all FastAPI router endpoints.
- Role attributes submitted in request payloads are ignored; user roles are derived strictly from database records.

## 3. Quiz Answer Protection
- `GET /api/quizzes/{id}/attempt` returns `ChildQuizAttemptResponse`, which strips `correct_answer` and `explanation` fields. Correct answers are never sent to the client prior to submission.
- All scoring logic is computed securely on the backend server.

## 4. Evaluation Data Isolation
- Synthetic development test data is flagged with `is_test_data = True`.
- `EvaluationDatasetExtractor` filters `is_test_data == False` by default to prevent development data from contaminating research evaluation metrics.

## 5. Security Test Suite
- Automated tests in `tests/test_backend_e2e.py` verify invalid token rejection, cross-child access rejection, unlinked parent access rejection, and admin boundary enforcement.
