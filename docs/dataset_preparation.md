# Dataset Preparation & Data Quality Audit

## 1. Primary Data Source

The primary source of learner interaction data for model training and evaluation is the system database containing:
- `LearningHistory`: Chronological records of lessons, activities, and quiz completions.
- `QuizAttempt` & `Answer`: Detailed quiz performance, accuracy percentages, and time taken.
- `ChildProfile`, `Topic`, `LearningContent`: Categorical attributes for difficulty levels and educational topics.

---

## 2. Interaction Features & Schema

Each extracted interaction record contains the following schema:

| Feature Name | Data Type | Description / Range |
|---|---|---|
| `child_id` | Integer | Unique identifier of the child learner. |
| `topic_id` | Integer | ID of the educational subject/topic. |
| `activity_type` | Categorical | `lesson`, `quiz`, `practice`, `activity`. |
| `difficulty` | Categorical | `easy`, `medium`, `hard`. |
| `score` | Float | Quiz/activity performance percentage ($0.0 - 100.0\%$). |
| `completion_status` | Categorical | `completed`, `in_progress`, `failed`. |
| `time_spent` | Float | Time spent on activity in seconds. |
| `timestamp` | Datetime (ISO) | Chronological timestamp of interaction. |

---

## 3. Data Quality Audit Results

The automated data quality audit script (`ml/data/data_quality.py`) checks for missing IDs, invalid categorical values, impossible scores, negative times, and duplicate records:

- **Total Records Audit**: 2 interaction records across 1 child learner profile.
- **Valid Records**: 2 ($100.0\%$).
- **Invalid / Missing / Out-of-Bounds Records**: 0.
- **Data Handling Policy**: Invalid records are flagged and excluded from PyTorch training sequence tensors without artificial imputation or fake data synthesis.

---

## 4. Chronological Splitting & Data Leakage Prevention

To prevent future performance metrics from leaking into previous input sequence windows:
1. Interactions for each learner are sorted strictly by `timestamp`.
2. Sequence windows of maximum length $N=20$ are constructed.
3. The dataset is split temporally:
   - **Train Split**: $70\%$ ($1$ record)
   - **Validation Split**: $15\%$
   - **Test Split**: $15\%$ ($1$ record)
