from typing import List, Dict, Any
from ml.evaluation.metrics import compute_strategy_metrics

class RuleBasedBaselineEvaluator:
    @staticmethod
    def evaluate_baseline(rule_based_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates Rule-Based Baseline strategy metrics."""
        metrics = compute_strategy_metrics(rule_based_records)
        metrics["strategy_name"] = "Rule-Based Baseline"
        return metrics
