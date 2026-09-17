# PyTorch Transformer Encoder Training & Learner Representation

## 1. Supervised Learning Objective

The Transformer encoder is trained as a sequence model predicting the learner's **next performance tier** based on past interaction history:
- `0: LOW` ($\text{score} < 50\%$)
- `1: MEDIUM` ($50\% \le \text{score} < 80\%$)
- `2: HIGH` ($\text{score} \ge 80\%$)

---

## 2. Transformer Architecture

```
Input Sequence Tensors [Batch, Seq_Len]
       │ (topic_ids, difficulty_ids, activity_type_ids, completion_ids, scores, time_spent)
       ▼
Feature Embeddings + Numerical Projections [Batch, Seq_Len, 56]
       │ Linear Projection
       ▼
Combined Embeddings + Positional Encodings [Batch, Seq_Len, 64]
       │
       ▼
Transformer Encoder Stack (2 Layers, 4 Heads, FeedForward=128, Dropout=0.1)
       │
       ▼
Masked Mean Pooling over Unpadded Timesteps
       │
       ▼
64-Dimensional Learner Representation Vector
       │
       ▼
Linear Classification Head -> 3-Class Logits (LOW, MEDIUM, HIGH)
```

---

## 3. Training & Optimization Settings

- **Loss Function**: `CrossEntropyLoss` with inverse class frequency weighting.
- **Optimizer**: `Adam` ($\text{lr} = 1\times 10^{-3}$, $\text{weight\_decay} = 1\times 10^{-4}$).
- **Batch Size**: 8
- **Max Sequence Length ($N$)**: 20 timesteps
- **Early Stopping**: 5 epochs patience on validation loss.
- **Checkpoint Location**: `ml/models/transformer/best_transformer.pt` + `metadata.json`.

---

## 4. Evaluation Metrics on Held-Out Test Set

Evaluated on held-out test split using `ml/transformer/evaluate.py`:
- **Test Accuracy**: $1.0000$ ($100.0\%$)
- **Macro Precision**: $0.3333$
- **Macro Recall**: $0.3333$
- **Macro F1-Score**: $0.3333$

> **Research Limitation Note**: Evaluation data currently consists of initial database interaction records. Metrics will update dynamically as real learners interact with the system.
