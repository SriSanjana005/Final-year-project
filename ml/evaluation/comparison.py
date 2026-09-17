from typing import Dict, Any, List

class StrategyComparator:
    @staticmethod
    def build_comparison_matrix(baseline_metrics: Dict[str, Any], proposed_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs a neutral side-by-side strategy comparison table.
        Avoids biased language ('winner', 'best', 'superior').
        """
        rows = []

        # Metric 1: Total Recommendations
        rows.append({
            "metric_name": "Recommendations Generated",
            "rule_based": str(baseline_metrics.get("total_recommendations", 0)),
            "transformer_ppo": str(proposed_metrics.get("total_recommendations", 0)),
            "unit": "Count"
        })

        # Metric 2: Total Learners
        rows.append({
            "metric_name": "Learners Represented",
            "rule_based": str(baseline_metrics.get("total_learners", 0)),
            "transformer_ppo": str(proposed_metrics.get("total_learners", 0)),
            "unit": "Count"
        })

        # Metric 3: View Rate
        rb_vr = baseline_metrics.get("view_rate")
        pr_vr = proposed_metrics.get("view_rate")
        rows.append({
            "metric_name": "Recommendation View Rate",
            "rule_based": f"{rb_vr}%" if isinstance(rb_vr, (int, float)) else str(rb_vr),
            "transformer_ppo": f"{pr_vr}%" if isinstance(pr_vr, (int, float)) else str(pr_vr),
            "unit": "%"
        })

        # Metric 4: Completion Rate
        rb_cr = baseline_metrics.get("completion_rate")
        pr_cr = proposed_metrics.get("completion_rate")
        rows.append({
            "metric_name": "Recommendation Completion Rate",
            "rule_based": f"{rb_cr}%" if isinstance(rb_cr, (int, float)) else str(rb_cr),
            "transformer_ppo": f"{pr_cr}%" if isinstance(pr_cr, (int, float)) else str(pr_cr),
            "unit": "%"
        })

        # Metric 5: Repeated Content Rate
        rb_rr = baseline_metrics.get("repeated_content_rate")
        pr_rr = proposed_metrics.get("repeated_content_rate")
        rows.append({
            "metric_name": "Repeated Content Rate",
            "rule_based": f"{rb_rr}%" if isinstance(rb_rr, (int, float)) else str(rb_rr),
            "transformer_ppo": f"{pr_rr}%" if isinstance(pr_rr, (int, float)) else str(pr_rr),
            "unit": "%"
        })

        # Metric 6: Difficulty Alignment Rate
        rb_da = baseline_metrics.get("difficulty_alignment_rate")
        pr_da = proposed_metrics.get("difficulty_alignment_rate")
        rows.append({
            "metric_name": "Difficulty Alignment Rate",
            "rule_based": f"{rb_da}%" if isinstance(rb_da, (int, float)) else str(rb_da),
            "transformer_ppo": f"{pr_da}%" if isinstance(pr_da, (int, float)) else str(pr_da),
            "unit": "%"
        })

        # Metric 7: Avg Subsequent Quiz Score
        rb_ss = baseline_metrics.get("subsequent_score_stats", {}).get("mean")
        pr_ss = proposed_metrics.get("subsequent_score_stats", {}).get("mean")
        rows.append({
            "metric_name": "Avg Subsequent Quiz Score",
            "rule_based": f"{rb_ss}%" if isinstance(rb_ss, (int, float)) else str(rb_ss),
            "transformer_ppo": f"{pr_ss}%" if isinstance(pr_ss, (int, float)) else str(pr_ss),
            "unit": "%"
        })

        # Metric 8: Avg Performance Change
        rb_pc = baseline_metrics.get("performance_change_stats", {}).get("mean")
        pr_pc = proposed_metrics.get("performance_change_stats", {}).get("mean")
        rows.append({
            "metric_name": "Avg Performance Change (Score Diff)",
            "rule_based": f"{rb_pc}%" if isinstance(rb_pc, (int, float)) else str(rb_pc),
            "transformer_ppo": f"{pr_pc}%" if isinstance(pr_pc, (int, float)) else str(pr_pc),
            "unit": "Percentage Points"
        })

        return {
            "comparison_matrix": rows,
            "interpretation_note": "Metrics reflect actual recorded database interaction records. Neutral side-by-side presentation."
        }
