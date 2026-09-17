# Transformer Architecture & Learner Representation Documentation

This document describes the lightweight PyTorch Transformer encoder architecture for modeling structured educational interaction sequences.

---

## 1. System Architecture Diagram

```
Learning History & Quiz Attempts
             │
             ▼
   SequenceBuilder (N=20)
             │
             ▼
      FeatureEncoder
             │
             ▼
┌───────────────────────────────────────────┐
│       LearnerTransformerEncoder           │
│                                           │
│ 1. Feature Embedding Layers               │
│    - Topic (16d), Diff (8d), Act (8d),    │
│      Comp (8d), Numerical Projection (16d)│
│                                           │
│ 2. Linear Feature Projection (56d -> 64d) │
│                                           │
│ 3. Learned Positional Embeddings          │
│                                           │
│ 4. PyTorch TransformerEncoder Stack       │
│    - 2 Layers, 4 Attention Heads          │
│                                           │
│ 5. Masked Mean Pooling over Timesteps     │
└───────────────────────────────────────────┘
             │
             ▼
  Learner Representation Vector (64-D)
             │
             ▼
  Future PPO Reinforcement Learning Agent
```

---

## 2. Hyperparameters & Configuration

Configured via `ml/transformer/config.py`:

- **Embedding Dimension ($d_{model}$)**: 64
- **Encoder Layers**: 2
- **Attention Heads**: 4
- **Feedforward Dimension**: 128
- **Dropout Rate**: 0.1
- **Max Sequence Length**: 20
- **Prediction Head**: 3 classes (`low`, `medium`, `high` performance tier prediction)

---

## 3. Embedding & Feature Concatenation

Each timestep's categorical and numerical features are embedded into vector spaces and concatenated:

$$E_{timestep} = [E_{topic} \parallel E_{difficulty} \parallel E_{activity} \parallel E_{completion} \parallel W_{num} \cdot [\text{score}, \text{time\_spent}]]$$

The combined 56-dimensional vector is projected via a linear layer into the 64-dimensional $d_{model}$ space before adding positional encodings and passing through `nn.TransformerEncoder`.

---

## 4. Masked Mean Pooling

To produce a single fixed-size 64-dimensional state representation vector $h_{learner} \in \mathbb{R}^{64}$ from the sequence outputs $H \in \mathbb{R}^{S \times 64}$:

$$h_{learner} = \frac{\sum_{i=1}^{S} (1 - m_i) \cdot H_i}{\sum_{i=1}^{S} (1 - m_i)}$$

where $m_i \in \{0, 1\}$ is the boolean padding mask ($1$ for padded steps, $0$ for valid steps).

---

## 5. Cold-Start Handling

For new learners with no recorded interactions ($S = 0$):
- `TransformerService` detects empty history and returns `model_status: "cold_start"`.
- The rule-based recommendation baseline handles introductory content selection without attempting un-fine-tuned neural inference.

---

## 6. Connection to Future PPO Agent

In future phases:
1. `learner_representation` ($64$-D vector) will serve as the input state vector $s_t \in \mathbb{R}^{64}$ for the PPO actor-critic network.
2. The PPO policy network $\pi(a_t | s_t)$ will select the optimal recommendation action $a_t$ from approved content.
