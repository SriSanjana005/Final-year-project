import sys
import os
import json
import torch
from torch.utils.data import DataLoader
from typing import Dict, Any

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config.training_config import config
from ml.transformer.config import TransformerConfig
from ml.transformer.model import LearnerTransformerEncoder
from ml.transformer.dataset import LearnerSequenceDataset

def compute_multiclass_metrics(y_true, y_pred, num_classes=3):
    """Calculates multiclass accuracy, precision, recall, F1, and confusion matrix."""
    matrix = [[0] * num_classes for _ in range(num_classes)]
    for t, p in zip(y_true, y_pred):
        if 0 <= t < num_classes and 0 <= p < num_classes:
            matrix[t][p] += 1

    total_samples = max(1, len(y_true))
    correct = sum(matrix[i][i] for i in range(num_classes))
    accuracy = correct / total_samples

    precisions = []
    recalls = []
    f1s = []

    for c in range(num_classes):
        tp = matrix[c][c]
        fp = sum(matrix[r][c] for r in range(num_classes) if r != c)
        fn = sum(matrix[c][p] for p in range(num_classes) if p != c)

        prec = tp / max(1, tp + fp)
        rec = tp / max(1, tp + fn)
        f1 = (2 * prec * rec) / max(1e-6, prec + rec)

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_precision = sum(precisions) / num_classes
    macro_recall = sum(recalls) / num_classes
    macro_f1 = sum(f1s) / num_classes

    return {
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1": round(macro_f1, 4),
        "confusion_matrix": matrix
    }

def evaluate_transformer_model():
    """
    Evaluates trained Transformer encoder on the held-out test split.
    Exports evaluation metrics to ml/models/transformer/evaluation_results.json.
    """
    test_split_path = os.path.join(config.PROCESSED_DATA_DIR, "test_split.json")
    checkpoint_path = os.path.join(config.TRANSFORMER_MODEL_DIR, "best_transformer.pt")

    if not os.path.exists(checkpoint_path):
        print("Notice: No trained Transformer checkpoint found for evaluation.")
        return {"status": "checkpoint_not_found", "message": "Transformer checkpoint missing."}

    if not os.path.exists(test_split_path):
        print("Notice: Test split file missing.")
        return {"status": "test_data_missing", "message": "Test split missing."}

    with open(test_split_path, "r", encoding="utf-8") as f:
        test_records = json.load(f)

    if not test_records:
        print("Notice: Test split contains 0 records.")
        return {"status": "test_data_empty", "message": "0 test records."}

    test_dataset = LearnerSequenceDataset(test_records, max_seq_len=config.MAX_SEQUENCE_LENGTH)
    if len(test_dataset) == 0:
        print("Notice: Test dataset sequence builder produced 0 samples.")
        return {"status": "insufficient_data", "message": "Test sequence dataset 0 samples."}

    test_loader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False)

    t_config = TransformerConfig()
    model = LearnerTransformerEncoder(t_config)
    
    try:
        model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
        model.eval()
    except Exception as e:
        print(f"Error loading checkpoint for evaluation: {e}")
        return {"status": "error", "message": str(e)}

    y_true = []
    y_pred = []

    with torch.no_grad():
        for batch in test_loader:
            targets = batch["target"]
            reps = model(batch)
            logits = model.predict_performance(reps)
            preds = logits.argmax(dim=-1)

            y_true.extend(targets.tolist())
            y_pred.extend(preds.tolist())

    metrics = compute_multiclass_metrics(y_true, y_pred, num_classes=config.NUM_CLASSES)
    
    results = {
        "evaluation_status": "evaluated",
        "timestamp": os.path.getmtime(checkpoint_path),
        "test_samples": len(y_true),
        "metrics": metrics,
        "class_labels": config.TARGET_CLASSES
    }

    eval_path = os.path.join(config.TRANSFORMER_MODEL_DIR, "evaluation_results.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Transformer Evaluation Completed ({len(y_true)} test samples): Accuracy={metrics['accuracy']:.4f}, Macro-F1={metrics['macro_f1']:.4f}")
    print(f"Evaluation results exported to {eval_path}")

    return results

if __name__ == "__main__":
    evaluate_transformer_model()
