import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any

class LearnerSequenceDataset(Dataset):
    def __init__(self, samples: List[Dict[str, Any]]):
        """
        samples is a list of dicts:
        {
          "encoded_features": dict of tensors (topic_ids, difficulty_ids, ...),
          "label": int (0: low, 1: medium, 2: high)
        }
        """
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int):
        sample = self.samples[idx]
        return sample["encoded_features"], torch.tensor(sample["label"], dtype=torch.long)
