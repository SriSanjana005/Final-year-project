import sys
import os
from typing import List, Dict, Any
import torch
from torch.utils.data import Dataset

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.data.feature_encoder import FeatureEncoder
from ml.config.training_config import config

def get_performance_tier(score: float) -> int:
    """Classifies percentage score into 0: LOW, 1: MEDIUM, 2: HIGH target categories."""
    if score < config.PERFORMANCE_LOW_THRESHOLD:
        return 0
    elif score < config.PERFORMANCE_MEDIUM_THRESHOLD:
        return 1
    return 2

class LearnerSequenceDataset(Dataset):
    """
    PyTorch Dataset for supervised Transformer training.
    Constructs chronological input sequence windows (length <= MAX_SEQUENCE_LENGTH)
    and maps the next interaction performance category as target.
    """
    def __init__(self, records: List[Dict[str, Any]], max_seq_len: int = config.MAX_SEQUENCE_LENGTH):
        self.max_seq_len = max_seq_len
        self.samples = []
        self.encoder = FeatureEncoder(max_seq_len=max_seq_len)
        self._build_samples(records)

    def _build_samples(self, records: List[Dict[str, Any]]):
        # Group records by child_id
        child_map: Dict[int, List[Dict[str, Any]]] = {}
        for r in records:
            cid = r.get("child_id")
            if not cid:
                continue
            if cid not in child_map:
                child_map[cid] = []
            child_map[cid].append(r)

        # For each child, build sliding sequence windows
        for cid, seq_list in child_map.items():
            seq_list.sort(key=lambda x: x.get("timestamp", ""))
            n = len(seq_list)
            
            if n < 2:
                # Cold start / 1 interaction sample
                input_seq = seq_list[:1]
                target_score = seq_list[0].get("score", 75.0)
                target_tier = get_performance_tier(target_score)
                self.samples.append((input_seq, target_tier))
            else:
                for i in range(1, n):
                    input_seq = seq_list[max(0, i - self.max_seq_len):i]
                    target_score = seq_list[i].get("score", 75.0)
                    target_tier = get_performance_tier(target_score)
                    self.samples.append((input_seq, target_tier))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        input_seq, target_label = self.samples[idx]
        tensors = self.encoder.encode_sequence(input_seq)
        
        # PyTorch Transformer padding mask expects bool (False = real token, True = pad)
        padding_mask = tensors["padding_mask"]
        
        return {
            "topic_ids": tensors["topic_ids"],
            "difficulty_ids": tensors["difficulty_ids"],
            "activity_type_ids": tensors["activity_type_ids"],
            "completion_ids": tensors["completion_ids"],
            "scores": tensors["scores"],
            "time_spent": tensors["time_spent"],
            "attention_mask": padding_mask,
            "target": torch.tensor(target_label, dtype=torch.long)
        }
