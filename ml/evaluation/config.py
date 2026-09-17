import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class EvaluationConfig:
    # 1. Reproducibility
    RANDOM_SEED: int = 42

    # 2. Evaluation Parameters
    MIN_OBSERVATIONS_FOR_STATS: int = 5
    CONFIDENCE_LEVEL: float = 0.95
    DATASET_VERSION: str = "1.0.0"

    # 3. Output Paths
    RESULTS_DIR: str = os.path.join(PROJECT_ROOT, "ml", "results")
    DOCS_RESULTS_DIR: str = os.path.join(PROJECT_ROOT, "docs", "results")

eval_config = EvaluationConfig()
