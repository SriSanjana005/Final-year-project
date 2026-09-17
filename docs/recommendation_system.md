# Recommendation System Architecture

## Overview
The recommendation system uses a dual-strategy architecture:
1. **Rule-Based Baseline Strategy**: Topic performance threshold rules (e.g. score < 50% $\rightarrow$ easy, 50-80% $\rightarrow$ same difficulty, > 80% $\rightarrow$ harder).
2. **Transformer + PPO Strategy**: Deep learning representation + Reinforcement Learning action policy.

---

## Decision Matrix (`AUTO` Mode)

```
                    Learner Request
                           |
            Check Completed Interactions
                           |
        +------------------+------------------+
        |                                     |
    < 3 Interactions                     >= 3 Interactions
        |                                     |
   COLD START                             Check Model
        |                                Checkpoints
        v                                     |
  RULE-BASED                      +-----------+-----------+
  STRATEGY                        |                       |
                             Models Available       Models Missing
                                  |                       |
                                  v                       v
                           TRANSFORMER + PPO         RULE-BASED
                               STRATEGY               FALLBACK
```

---

## PPO Action Mapping
PPO policy outputs discrete action index:
- `0`: `REVIEW_PREVIOUS_TOPIC` $\rightarrow$ Practice activity on previous topic
- `1`: `EASIER_CONTENT` $\rightarrow$ Lower difficulty module
- `2`: `SAME_DIFFICULTY` $\rightarrow$ Same difficulty module
- `3`: `HARDER_CONTENT` $\rightarrow$ Higher difficulty module
- `4`: `PRACTICE_CONTENT` $\rightarrow$ Interactive practice activity

Every selected action is passed to `ContentSelectionService`, which guarantees that ONLY published, admin-approved content is selected.
