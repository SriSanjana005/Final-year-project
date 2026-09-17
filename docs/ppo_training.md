# PPO Reinforcement Learning Policy Training

## 1. PPO Policy Architecture

The PPO (Proximal Policy Optimization) agent selects discrete content adaptation actions based on a 68-dimensional state vector combining the Transformer representation and contextual learner metrics.

---

## 2. 68-D State Space Vector

$$\mathbf{s} = \left[ \mathbf{v}_{\text{Transformer}} \in \mathbb{R}^{64}, \; \bar{S}_{\text{recent}}, \; C_{\text{rate}}, \; T_{\text{recent}}, \; D_{\text{current}} \right] \in \mathbb{R}^{68}$$

---

## 3. Discrete Action Space ($A \in \{0, 1, 2, 3, 4\}$)

| Action Code | Action Name | Recommendation Target Criteria |
|---|---|---|
| `0` | `REVIEW_PREVIOUS_TOPIC` | Recommends review content from a previously studied topic. |
| `1` | `EASIER_CONTENT` | Recommends lower difficulty content (`easy`). |
| `2` | `SAME_DIFFICULTY` | Recommends content matching current difficulty. |
| `3` | `HARDER_CONTENT` | Recommends higher difficulty content (`medium`/`hard`). |
| `4` | `PRACTICE_CONTENT` | Recommends interactive practice modules. |

---

## 4. Hyperparameters & Training Setup

- **RL Framework**: Stable-Baselines3 PPO (`MlpPolicy`)
- **Environment**: `LearnerRecommendationEnv` (Gymnasium)
- **Total Timesteps**: 10,000
- **Learning Rate**: $3 \times 10^{-4}$
- **Discount Factor ($\gamma$)**: 0.99
- **GAE Lambda ($\lambda$)**: 0.95
- **Clip Range**: 0.2
- **Entropy Coefficient**: 0.01
- **Checkpoint Paths**: `ml/models/ppo/ppo_recommendation_agent.zip` & `ml/models/ppo_recommendation_agent.zip`.

---

## 5. Evaluation Results

Evaluated over 50 test episodes:
- **Mean Episode Reward**: $7.3000 \pm 0.0000$
- **Environment Label**: `DEVELOPMENT-ONLY — Observational Replay Evaluation`
