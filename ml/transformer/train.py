import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from ml.config.training_config import config
from ml.transformer.config import TransformerConfig
from ml.transformer.model import LearnerTransformerEncoder
from ml.transformer.dataset import LearnerSequenceDataset
from ml.data.split_dataset import split_learner_dataset

def set_seed(seed: int = config.RANDOM_SEED):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_class_weights(targets: List[int], num_classes: int = 3) -> torch.Tensor:
    counts = [0] * num_classes
    for t in targets:
        if 0 <= t < num_classes:
            counts[t] += 1
    total = max(1, len(targets))
    weights = [total / max(1, count) for count in counts]
    # Normalize weights
    max_w = max(weights)
    norm_weights = [w / max_w for w in weights]
    return torch.tensor(norm_weights, dtype=torch.float32)

def train_transformer_model():
    """
    Supervised Transformer training pipeline.
    Loads train and val splits, computes class imbalance weights, tracks loss/accuracy,
    enforces early stopping, and exports checkpoint + metadata.
    """
    set_seed(config.RANDOM_SEED)

    train_split_path = os.path.join(config.PROCESSED_DATA_DIR, "train_split.json")
    val_split_path = os.path.join(config.PROCESSED_DATA_DIR, "val_split.json")

    if not os.path.exists(train_split_path) or not os.path.exists(val_split_path):
        train_records, val_records, _ = split_learner_dataset()
    else:
        with open(train_split_path, "r", encoding="utf-8") as f:
            train_records = json.load(f)
        with open(val_split_path, "r", encoding="utf-8") as f:
            val_records = json.load(f)

    if not train_records:
        print("Notice: No training records available for Transformer training.")
        return {"training_status": "insufficient_data", "message": "No training interaction records."}

    train_dataset = LearnerSequenceDataset(train_records, max_seq_len=config.MAX_SEQUENCE_LENGTH)
    val_dataset = LearnerSequenceDataset(val_records, max_seq_len=config.MAX_SEQUENCE_LENGTH) if val_records else None

    if len(train_dataset) == 0:
        print("Notice: Sequence dataset builder produced 0 sequence samples.")
        return {"training_status": "insufficient_data", "message": "Sequence dataset yielded 0 samples."}

    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False) if val_dataset and len(val_dataset) > 0 else None

    # Class imbalance calculation
    train_targets = [s[1] for s in train_dataset.samples]
    class_counts = {0: train_targets.count(0), 1: train_targets.count(1), 2: train_targets.count(2)}
    class_weights = compute_class_weights(train_targets, num_classes=config.NUM_CLASSES)

    t_config = TransformerConfig()
    model = LearnerTransformerEncoder(t_config)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY)

    best_val_loss = float("inf")
    patience_counter = 0
    history_metrics = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    os.makedirs(config.TRANSFORMER_MODEL_DIR, exist_ok=True)
    checkpoint_path = os.path.join(config.TRANSFORMER_MODEL_DIR, "best_transformer.pt")

    for epoch in range(config.EPOCHS):
        # --- Training Loop ---
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch in train_loader:
            targets = batch["target"]
            optimizer.zero_grad()
            reps = model(batch)
            logits = model.predict_performance(reps)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * targets.size(0)
            preds = logits.argmax(dim=-1)
            train_correct += (preds == targets).sum().item()
            train_total += targets.size(0)

        epoch_train_loss = train_loss / max(1, train_total)
        epoch_train_acc = train_correct / max(1, train_total)

        # --- Validation Loop ---
        val_loss = epoch_train_loss
        val_acc = epoch_train_acc
        if val_loader:
            model.eval()
            v_loss = 0.0
            v_correct = 0
            v_total = 0
            with torch.no_grad():
                for batch in val_loader:
                    targets = batch["target"]
                    reps = model(batch)
                    logits = model.predict_performance(reps)
                    loss = criterion(logits, targets)
                    v_loss += loss.item() * targets.size(0)
                    preds = logits.argmax(dim=-1)
                    v_correct += (preds == targets).sum().item()
                    v_total += targets.size(0)
            val_loss = v_loss / max(1, v_total)
            val_acc = v_correct / max(1, v_total)

        history_metrics["train_loss"].append(round(epoch_train_loss, 4))
        history_metrics["val_loss"].append(round(val_loss, 4))
        history_metrics["train_acc"].append(round(epoch_train_acc, 4))
        history_metrics["val_acc"].append(round(val_acc, 4))

        print(f"Epoch [{epoch+1}/{config.EPOCHS}] Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.4f} | Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")

        # Checkpoint Best Model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), checkpoint_path)
        else:
            patience_counter += 1
            if patience_counter >= config.EARLY_STOPPING_PATIENCE:
                print(f"Early stopping triggered at epoch {epoch+1}")
                break

    metadata = {
        "training_status": "trained",
        "timestamp": datetime.utcnow().isoformat(),
        "random_seed": config.RANDOM_SEED,
        "epochs_run": len(history_metrics["train_loss"]),
        "train_samples": len(train_dataset),
        "val_samples": len(val_dataset) if val_dataset else 0,
        "class_counts": class_counts,
        "final_train_loss": history_metrics["train_loss"][-1],
        "final_val_loss": history_metrics["val_loss"][-1],
        "final_train_acc": history_metrics["train_acc"][-1],
        "final_val_acc": history_metrics["val_acc"][-1],
        "history": history_metrics,
        "checkpoint_path": checkpoint_path
    }

    meta_path = os.path.join(config.TRANSFORMER_MODEL_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Successfully trained Transformer encoder! Checkpoint saved to {checkpoint_path}")
    return metadata

if __name__ == "__main__":
    train_transformer_model()
