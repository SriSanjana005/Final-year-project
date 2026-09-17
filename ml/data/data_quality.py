import sys
import os
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config.training_config import config
from ml.data.extract_dataset import extract_learner_interactions

def run_data_quality_audit(records=None):
    """
    Performs data quality audit on extracted learner interaction dataset.
    Identifies missing fields, impossible scores, negative times, and duplicate records.
    """
    if records is None:
        json_path = os.path.join(config.PROCESSED_DATA_DIR, "learner_interactions.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        else:
            records = extract_learner_interactions()

    total_records = len(records)
    missing_child_ids = 0
    missing_topic_ids = 0
    invalid_difficulty_counts = 0
    invalid_activity_type_counts = 0
    impossible_score_counts = 0
    negative_time_spent_counts = 0
    invalid_timestamps = 0
    duplicate_records = 0

    seen_signatures = set()
    valid_records = 0
    valid_records_list = []

    valid_difficulties = {"easy", "medium", "hard"}
    valid_activity_types = {"lesson", "quiz", "practice", "activity"}

    for r in records:
        is_valid = True

        if not r.get("child_id"):
            missing_child_ids += 1
            is_valid = False

        if not r.get("topic_id"):
            missing_topic_ids += 1
            is_valid = False

        if r.get("difficulty") not in valid_difficulties:
            invalid_difficulty_counts += 1
            is_valid = False

        if r.get("activity_type") not in valid_activity_types:
            invalid_activity_type_counts += 1
            is_valid = False

        score = r.get("score")
        if score is None or score < 0.0 or score > 100.0:
            impossible_score_counts += 1
            is_valid = False

        time_spent = r.get("time_spent")
        if time_spent is None or time_spent < 0.0:
            negative_time_spent_counts += 1
            is_valid = False

        sig = (r.get("child_id"), r.get("topic_id"), r.get("activity_type"), r.get("timestamp"))
        if sig in seen_signatures:
            duplicate_records += 1
            is_valid = False
        else:
            seen_signatures.add(sig)

        if is_valid:
            valid_records += 1
            valid_records_list.append(r)

    children_represented = len(set(r.get("child_id") for r in valid_records_list if r.get("child_id")))
    topics_represented = len(set(r.get("topic_id") for r in valid_records_list if r.get("topic_id")))

    report = {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": total_records - valid_records,
        "missing_child_ids": missing_child_ids,
        "missing_topic_ids": missing_topic_ids,
        "invalid_difficulty_counts": invalid_difficulty_counts,
        "invalid_activity_type_counts": invalid_activity_type_counts,
        "impossible_score_counts": impossible_score_counts,
        "negative_time_spent_counts": negative_time_spent_counts,
        "duplicate_records": duplicate_records,
        "children_represented": children_represented,
        "topics_represented": topics_represented,
        "handling_strategy": "Invalid records are flagged and excluded from PyTorch training sequence tensors without artificial imputation."
    }

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    report_path = os.path.join(config.RESULTS_DIR, "data_quality_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Data Quality Audit Completed: {valid_records}/{total_records} valid records.")
    print(f"Quality report exported to {report_path}")

    return report, valid_records_list

if __name__ == "__main__":
    run_data_quality_audit()
