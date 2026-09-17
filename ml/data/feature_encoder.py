from typing import List, Dict, Any, Tuple
import torch

# Vocabulary Encodings (Index 0 reserved for <pad>)
DIFFICULTY_MAP = {"<pad>": 0, "easy": 1, "medium": 2, "hard": 3}
ACTIVITY_TYPE_MAP = {"<pad>": 0, "quiz": 1, "lesson": 2, "practice": 3, "activity": 4}
COMPLETION_MAP = {"<pad>": 0, "completed": 1, "in_progress": 2, "failed": 3}

class FeatureEncoder:
    def __init__(self, max_seq_len: int = 20):
        self.max_seq_len = max_seq_len

    def encode_sequence(self, sequence: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """
        Encodes a list of interaction dictionaries into PyTorch tensors with fixed length padding.
        Returns tensor dict ready for model forward pass.
        """
        seq_length = len(sequence)
        pad_count = self.max_seq_len - seq_length

        topic_ids = []
        difficulty_ids = []
        activity_type_ids = []
        completion_ids = []
        scores = []
        time_spents = []
        padding_mask = [] # True for padded tokens, False for real interaction tokens

        # Left-pad sequence up to max_seq_len
        for _ in range(pad_count):
            topic_ids.append(0)
            difficulty_ids.append(0)
            activity_type_ids.append(0)
            completion_ids.append(0)
            scores.append(0.0)
            time_spents.append(0.0)
            padding_mask.append(True)

        for item in sequence:
            t_id = int(item.get("topic_id", 1))
            diff_str = str(item.get("difficulty", "easy")).lower()
            diff_id = DIFFICULTY_MAP.get(diff_str, 1)
            
            act_str = str(item.get("activity_type", "lesson")).lower()
            act_id = ACTIVITY_TYPE_MAP.get(act_str, 2)
            
            comp_str = str(item.get("completion_status", "completed")).lower()
            comp_id = COMPLETION_MAP.get(comp_str, 1)

            raw_score = float(item.get("score", 0.0))
            norm_score = max(0.0, min(1.0, raw_score / 100.0))

            raw_time = float(item.get("time_spent", 60))
            norm_time = max(0.0, min(1.0, raw_time / 300.0)) # Normalized over 5 mins

            topic_ids.append(t_id)
            difficulty_ids.append(diff_id)
            activity_type_ids.append(act_id)
            completion_ids.append(comp_id)
            scores.append(norm_score)
            time_spents.append(norm_time)
            padding_mask.append(False)

        # Convert to PyTorch Tensors
        return {
            "topic_ids": torch.tensor(topic_ids, dtype=torch.long),
            "difficulty_ids": torch.tensor(difficulty_ids, dtype=torch.long),
            "activity_type_ids": torch.tensor(activity_type_ids, dtype=torch.long),
            "completion_ids": torch.tensor(completion_ids, dtype=torch.long),
            "scores": torch.tensor(scores, dtype=torch.float32),
            "time_spent": torch.tensor(time_spents, dtype=torch.float32),
            "padding_mask": torch.tensor(padding_mask, dtype=torch.bool)
        }
