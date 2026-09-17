import os
import sys
import torch
import torch.nn as nn

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from ml.transformer.config import TransformerConfig

class LearnerTransformerEncoder(nn.Module):
    def __init__(self, config: TransformerConfig = TransformerConfig()):
        super().__init__()
        self.config = config

        d_model = config.embedding_dim

        # 1. Feature Embedding Layers
        self.topic_embed = nn.Embedding(config.num_topics, d_model // 4, padding_idx=0)
        self.difficulty_embed = nn.Embedding(config.num_difficulties, d_model // 8, padding_idx=0)
        self.activity_embed = nn.Embedding(config.num_activity_types, d_model // 8, padding_idx=0)
        self.completion_embed = nn.Embedding(config.num_completion_statuses, d_model // 8, padding_idx=0)
        
        # 2. Numerical Features Projection (score, time_spent -> 16 dim)
        self.num_proj = nn.Linear(2, d_model // 4)

        # Total combined features dim: 16 + 8 + 8 + 8 + 16 = 56
        combined_dim = (d_model // 4) + (d_model // 8) + (d_model // 8) + (d_model // 8) + (d_model // 4)
        self.feature_proj = nn.Linear(combined_dim, d_model)

        # 3. Learned Positional Embeddings
        self.pos_embed = nn.Embedding(config.max_seq_length, d_model)

        # 4. Transformer Encoder Stack
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=config.num_heads,
            dim_feedforward=config.feedforward_dim,
            dropout=config.dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=config.num_layers)

        # 5. Optional Supervised Classification Head (predicting low/medium/high next performance)
        self.classifier = nn.Linear(d_model, config.num_classes)

    def forward(self, batch: dict) -> torch.Tensor:
        """
        Forward pass converting feature tensors into 64-dim learner representation.
        Expects keys: topic_ids, difficulty_ids, activity_type_ids, completion_ids, scores, time_spent, padding_mask
        """
        topic_ids = batch["topic_ids"]           # [B, S]
        diff_ids = batch["difficulty_ids"]        # [B, S]
        act_ids = batch["activity_type_ids"]      # [B, S]
        comp_ids = batch["completion_ids"]        # [B, S]
        scores = batch["scores"].unsqueeze(-1)    # [B, S, 1]
        times = batch["time_spent"].unsqueeze(-1) # [B, S, 1]
        padding_mask = batch.get("padding_mask", batch.get("attention_mask"))      # [B, S] (True = padded)

        batch_size, seq_len = topic_ids.shape

        # Embed categorical & numerical features
        e_topic = self.topic_embed(topic_ids)
        e_diff = self.difficulty_embed(diff_ids)
        e_act = self.activity_embed(act_ids)
        e_comp = self.completion_embed(comp_ids)

        num_features = torch.cat([scores, times], dim=-1) # [B, S, 2]
        e_num = self.num_proj(num_features)               # [B, S, 16]

        # Combine all features
        combined = torch.cat([e_topic, e_diff, e_act, e_comp, e_num], dim=-1) # [B, S, 56]
        x = self.feature_proj(combined)                                         # [B, S, 64]

        # Add Positional Encodings
        positions = torch.arange(seq_len, device=topic_ids.device).unsqueeze(0).expand(batch_size, seq_len)
        x = x + self.pos_embed(positions)

        # Transformer Encoder Stack
        # src_key_padding_mask: True indicates padded steps to be masked
        out = self.transformer_encoder(x, src_key_padding_mask=padding_mask) # [B, S, 64]

        # Masked Mean Pooling over unpadded sequence timesteps
        valid_mask = (~padding_mask).unsqueeze(-1).float() # [B, S, 1] (1 for valid, 0 for padded)
        sum_embeddings = torch.sum(out * valid_mask, dim=1)  # [B, 64]
        valid_counts = torch.clamp(valid_mask.sum(dim=1), min=1.0) # [B, 1]
        
        learner_representation = sum_embeddings / valid_counts # [B, 64]

        return learner_representation

    def predict_performance(self, learner_representation: torch.Tensor) -> torch.Tensor:
        """Projects 64-dim learner representation to 3-class logits (low, medium, high)."""
        return self.classifier(learner_representation)
