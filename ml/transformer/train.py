import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import List, Dict, Any, Optional
from ml.transformer.config import TransformerConfig
from ml.transformer.model import LearnerTransformerEncoder
from ml.transformer.dataset import LearnerSequenceDataset

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml", "models")

def train_transformer_model(
    dataset_samples: List[Dict[str, Any]],
    epochs: int = 5,
    batch_size: int = 4,
    lr: float = 1e-3,
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Supervised training routine predicting next learner performance category (low, medium, high).
    Saves trained PyTorch checkpoint to save_path.
    """
    if not dataset_samples:
        return {"status": "insufficient_data", "message": "No training samples provided."}

    os.makedirs(MODEL_DIR, exist_ok=True)
    if not save_path:
        save_path = os.path.join(MODEL_DIR, "learner_transformer.pt")

    config = TransformerConfig()
    model = LearnerTransformerEncoder(config)
    model.train()

    dataset = LearnerSequenceDataset(dataset_samples)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    epoch_losses = []

    for epoch in range(epochs):
        running_loss = 0.0
        for features, labels in dataloader:
            optimizer.zero_grad()

            # Forward pass: extract learner state representation
            representations = model(features) # [B, 64]
            logits = model.predict_performance(representations) # [B, 3]

            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_loss = running_loss / max(1, len(dataloader))
        epoch_losses.append(avg_loss)
        print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f}")

    # Save model checkpoint
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "config": {
            "embedding_dim": config.embedding_dim,
            "num_layers": config.num_layers,
            "num_heads": config.num_heads,
            "feedforward_dim": config.feedforward_dim,
            "max_seq_length": config.max_seq_length
        },
        "final_loss": epoch_losses[-1] if epoch_losses else 0.0
    }
    torch.save(checkpoint, save_path)
    print(f"Saved Transformer model checkpoint to {save_path}")

    return {
        "status": "success",
        "checkpoint_path": save_path,
        "epochs_completed": epochs,
        "final_loss": epoch_losses[-1] if epoch_losses else 0.0
    }

if __name__ == "__main__":
    print("Training module loaded successfully. Run with a collected dataset to fine-tune checkpoint.")
