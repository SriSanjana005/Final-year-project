import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import List, Dict, Any
from ml.transformer.model import LearnerTransformerEncoder
from ml.transformer.dataset import LearnerSequenceDataset

def evaluate_transformer_model(
    model: LearnerTransformerEncoder,
    test_samples: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates model prediction accuracy on a test dataset split.
    """
    if not test_samples:
        return {"status": "insufficient_data", "accuracy": 0.0, "total_samples": 0}

    model.eval()
    dataset = LearnerSequenceDataset(test_samples)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False)

    correct = 0
    total = 0
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0

    with torch.no_grad():
        for features, labels in dataloader:
            representations = model(features)
            logits = model.predict_performance(representations)
            loss = criterion(logits, labels)

            total_loss += loss.item()
            preds = torch.argmax(logits, dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    accuracy = (correct / total * 100.0) if total > 0 else 0.0
    avg_loss = total_loss / max(1, len(dataloader))

    return {
        "status": "success",
        "total_samples": total,
        "correct_predictions": correct,
        "accuracy_percentage": round(accuracy, 2),
        "average_loss": round(avg_loss, 4)
    }
