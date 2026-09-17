# ML Data Pipeline Documentation

This document describes the design and specification of the machine learning data pipeline for the **Transformer-Based Personalized Learning Recommendation System for Children with Special Needs**.

---

## 1. Interaction Event Features

Each learning interaction extracted from `LearningHistory` and `QuizAttempt` is represented as a structured sequence item:

| Feature Name | Type | Processing / Normalization | Vector / Index Mapping |
|---|---|---|---|
| `topic_id` | Categorical | Mapped to Integer Vocabulary Index | Index $0$ reserved for `<pad>` |
| `difficulty` | Categorical | Mapped to Integer Index | `{"<pad>": 0, "easy": 1, "medium": 2, "hard": 3}` |
| `activity_type` | Categorical | Mapped to Integer Index | `{"<pad>": 0, "quiz": 1, "lesson": 2, "practice": 3, "activity": 4}` |
| `completion_status` | Categorical | Mapped to Integer Index | `{"<pad>": 0, "completed": 1, "in_progress": 2, "failed": 3}` |
| `score` | Numerical | Normalized float $\in [0.0, 1.0]$ | `score / 100.0` |
| `time_spent` | Numerical | Normalized float $\in [0.0, 1.0]$ | `min(1.0, time_spent / 300.0)` (5 min scale) |

---

## 2. Sequence Window & Padding

- **Max Sequence Length**: `MAX_SEQUENCE_LENGTH = 20`
- **Chronological Ordering**: Events are sorted by `timestamp` ascending (oldest to newest).
- **Truncation**: For children with $> 20$ interactions, the most recent 20 events are retained.
- **Padding**: Sequences with $< 20$ events are left-padded with `<pad>` token indices ($0$) and $0.0$ numerical values.
- **Attention / Padding Mask**: Generates a boolean PyTorch tensor `padding_mask` of shape `[batch_size, 20]`, where `True` indicates a padded step and `False` indicates a valid interaction step.

---

## 3. Pipeline Modules

### `ml/data/sequence_builder.py`
- Extracts records from `LearningHistory` and `QuizAttempt`.
- Merges and sorts records chronologically.
- Enforces `MAX_SEQUENCE_LENGTH = 20`.
- Detects cold-start state if sequence is empty.

### `ml/data/feature_encoder.py`
- Converts raw event sequence dictionaries into PyTorch `torch.Tensor` objects:
  - `topic_ids`: `torch.long`
  - `difficulty_ids`: `torch.long`
  - `activity_type_ids`: `torch.long`
  - `completion_ids`: `torch.long`
  - `scores`: `torch.float32`
  - `time_spent`: `torch.float32`
  - `padding_mask`: `torch.bool`
