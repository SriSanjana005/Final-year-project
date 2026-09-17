import os
import torch
from typing import Dict, Any, Optional
from ml.transformer.config import TransformerConfig
from ml.transformer.model import LearnerTransformerEncoder
from ml.data.feature_encoder import FeatureEncoder

CHECKPOINT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml", "models", "learner_transformer.pt")

class LearnerStateExtractor:
    def __init__(self, checkpoint_path: Optional[str] = CHECKPOINT_PATH):
        self.config = TransformerConfig()
        self.encoder = LearnerTransformerEncoder(self.config)
        self.encoder.eval()

        # Load weights if checkpoint exists
        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                if "model_state_dict" in ckpt:
                    self.encoder.load_state_dict(ckpt["model_state_dict"])
                else:
                    self.encoder.load_state_dict(ckpt)
                print(f"Loaded Transformer checkpoint from {checkpoint_path}")
            except Exception as e:
                print(f"Notice: Running un-fine-tuned PyTorch Transformer architecture: {e}")

    def extract_representation(self, encoded_batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        Accepts preprocessed tensors for a single learner sequence, adds batch dimension if needed,
        runs model forward pass, and returns 64-dim learner representation.
        """
        # Ensure batch dimension [1, seq_len]
        batch = {}
        for k, v in encoded_batch.items():
            if v.dim() == 1:
                batch[k] = v.unsqueeze(0)
            else:
                batch[k] = v

        with torch.no_grad():
            representation_tensor = self.encoder(batch) # [1, 64]
            logits = self.encoder.predict_performance(representation_tensor) # [1, 3]
            predicted_tier_idx = torch.argmax(logits, dim=-1).item()

        representation_vector = representation_tensor.squeeze(0).tolist()
        tier_map = {0: "low", 1: "medium", 2: "high"}

        return {
            "representation_dim": len(representation_vector),
            "learner_representation": representation_vector,
            "predicted_performance_tier": tier_map.get(predicted_tier_idx, "medium")
        }
