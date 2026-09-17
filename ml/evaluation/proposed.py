from typing import List, Dict, Any
from ml.evaluation.metrics import compute_strategy_metrics

class TransformerPPOProposedEvaluator:
    @staticmethod
    def evaluate_proposed(proposed_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates Transformer + PPO Proposed strategy metrics."""
        metrics = compute_strategy_metrics(proposed_records)
        metrics["strategy_name"] = "Transformer + PPO System"
        return metrics
