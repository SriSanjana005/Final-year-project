# PPO Reinforcement Learning Architecture Documentation

This document describes the design and specification of the **Proximal Policy Optimization (PPO)** Reinforcement Learning recommendation engine for the *Transformer-Based Personalized Learning Recommendation System for Children with Special Needs*.

---

## 1. System Architecture Diagram

```
                 Learning History
                       │
                       ▼
                Sequence Builder
                       │
                       ▼
                  Transformer
                       │
              Learner Representation (64-D)
                       │
                       ▼
            LearnerStateAdapter (+4 Contextual Features)
                       │
                       ▼
              RL State Vector (68-D)
                       │
                       ▼
                  PPO Agent
                       │
                Discrete Action (0-4)
                       │
          Approved Content Selection
                       │
                 Child Activity
                       │
             Performance / Feedback
                       │
                    Reward
                       │
                  Updated State
```

---

## 2. Discrete Action Space ($A \in \{0, 1, 2, 3, 4\}$)

Configured in `ml/reinforcement_learning/actions.py`:

| Action ID | Action Name | Category & Content Selection Criteria |
|---|---|---|
| `0` | `REVIEW_PREVIOUS_TOPIC` | Recommends review/practice content for previous completed topic. |
| `1` | `EASIER_CONTENT` | Recommends lower difficulty content in current learning topic (`easy`). |
| `2` | `SAME_DIFFICULTY` | Recommends same difficulty content in current learning topic. |
| `3` | `HARDER_CONTENT` | Recommends higher difficulty content in current learning topic (`medium`/`hard`). |
| `4` | `PRACTICE_CONTENT` | Recommends interactive practice/activity content (`content_type="practice"`). |

> **Crucial Requirement**: The PPO agent selects discrete action criteria ($0-4$) ONLY. It does **NOT** generate educational content or quiz questions. Content is served strictly from the admin-approved library.

---

## 3. RL State Vector Construction (68-D)

Configured in `ml/reinforcement_learning/policy.py`:

$$s_t = [h_{\text{transformer}}(64\text{-D}) \parallel \text{score}_{\text{norm}} \parallel \text{completion}_{\text{norm}} \parallel \text{time}_{\text{norm}} \parallel \text{diff}_{\text{norm}} ] \in \mathbb{R}^{68}$$

- `gymnasium.spaces.Box(low=-inf, high=inf, shape=(68,), dtype=np.float32)`

---

## 4. Transparent Reward Function

Configured in `ml/reinforcement_learning/reward.py`:

$$\text{Reward} = R_{\text{improvement}} + R_{\text{completion}} + R_{\text{engagement}} - P_{\text{inappropriate\_difficulty}}$$

- **Performance Improvement**: $w_{\text{improvement}} \cdot (\Delta \text{score} / 100.0)$
- **Completion Signal**: $+0.5$ for completed activities, $-0.2$ for incomplete items.
- **Engagement Signal**: $+0.2$ for active duration $\ge 30$ seconds.
- **Difficulty Penalty**: $-0.5$ for inappropriate difficulty assignments (e.g., beginner learner assigned hard content).

---

## 5. Fallback Mechanism

The architecture uses a strategy fallback hierarchy:

$$\text{Learner Request} \longrightarrow \begin{cases} \text{Cold Start / Insufficient History} \longrightarrow \text{Rule-Based Baseline Strategy} \\ \text{PPO Model Absent / Unreachable} \longrightarrow \text{Rule-Based Baseline Strategy} \\ \text{Valid State + Active Checkpoint} \longrightarrow \text{Transformer + PPO Strategy} \end{cases}$$

Every recommendation record persists its generation strategy in the database (`recommendation_type = "transformer_ppo"` vs `"rule_based"`).

---

## 6. Research Boundaries & Ethics

- The model recommends strictly from administrator-approved learning resources.
- The system is **NOT** a medical diagnostic tool or disability classifier.
- Real children are **NEVER** used directly as an uncontrolled RL exploration environment.
