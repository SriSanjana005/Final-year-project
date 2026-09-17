import sys
import os
import json
import random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config.training_config import config
from ml.data.data_quality import run_data_quality_audit

def split_learner_dataset(valid_records=None, train_ratio=config.TRAIN_RATIO, val_ratio=config.VALIDATION_RATIO):
    """
    Performs per-child chronological dataset split to ensure strict Data Leakage Prevention.
    Earlier interactions -> TRAIN, middle -> VALIDATION, latest -> TEST.
    Prevents future interaction values from leaking into sequence input windows.
    """
    if valid_records is None:
        _, valid_records = run_data_quality_audit()

    # Group valid records by child_id
    child_records_map = {}
    for r in valid_records:
        cid = r["child_id"]
        if cid not in child_records_map:
            child_records_map[cid] = []
        child_records_map[cid].append(r)

    train_records = []
    val_records = []
    test_records = []

    # Sort each child's interactions chronologically and split by temporal ratio
    for cid, records_list in child_records_map.items():
        records_list.sort(key=lambda x: x["timestamp"])
        n = len(records_list)
        
        if n == 1:
            train_records.extend(records_list)
        elif n == 2:
            train_records.append(records_list[0])
            test_records.append(records_list[1])
        else:
            n_train = max(1, int(n * train_ratio))
            n_val = max(1, int(n * val_ratio))
            train_sub = records_list[:n_train]
            val_sub = records_list[n_train:n_train + n_val]
            test_sub = records_list[n_train + n_val:]

            train_records.extend(train_sub)
            val_records.extend(val_sub if val_sub else records_list[n_train:n_train+1])
            test_records.extend(test_sub if test_sub else records_list[-1:])

    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    
    with open(os.path.join(config.PROCESSED_DATA_DIR, "train_split.json"), "w", encoding="utf-8") as f:
        json.dump(train_records, f, indent=2)

    with open(os.path.join(config.PROCESSED_DATA_DIR, "val_split.json"), "w", encoding="utf-8") as f:
        json.dump(val_records, f, indent=2)

    with open(os.path.join(config.PROCESSED_DATA_DIR, "test_split.json"), "w", encoding="utf-8") as f:
        json.dump(test_records, f, indent=2)

    print(f"Dataset Chronological Split Completed:")
    print(f"  TRAIN Records: {len(train_records)}")
    print(f"  VAL Records:   {len(val_records)}")
    print(f"  TEST Records:  {len(test_records)}")

    return train_records, val_records, test_records

if __name__ == "__main__":
    split_learner_dataset()
