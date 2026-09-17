import os
import sys
import json
import csv
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.evaluation.config import eval_config
from ml.evaluation.dataset import EvaluationDatasetExtractor
from ml.evaluation.baseline import RuleBasedBaselineEvaluator
from ml.evaluation.proposed import TransformerPPOProposedEvaluator
from ml.evaluation.comparison import StrategyComparator
from ml.evaluation.report import EvaluationReportGenerator
from ml.evaluation.visualization import generate_comparison_plots

def run_evaluation_pipeline(db=None):
    """
    Executes complete experimental evaluation pipeline:
    Extracts strategy datasets -> Computes baseline & proposed metrics -> Builds comparison matrix -> 
    Renders plots -> Exports JSON, CSV, and Markdown report.
    """
    print("Initiating Experimental Evaluation Pipeline...")

    # 1. Extract strategy-separated evaluation records and safety audit
    rb_records, pr_records, safety_audit = EvaluationDatasetExtractor.extract_evaluation_records(db)

    # 2. Evaluate Baseline Strategy
    baseline_metrics = RuleBasedBaselineEvaluator.evaluate_baseline(rb_records)

    # 3. Evaluate Proposed Transformer + PPO Strategy
    proposed_metrics = TransformerPPOProposedEvaluator.evaluate_proposed(pr_records)

    # 4. Build Neutral Side-by-Side Comparison Matrix
    comparison_res = StrategyComparator.build_comparison_matrix(baseline_metrics, proposed_metrics)
    comparison_matrix = comparison_res["comparison_matrix"]

    # 5. Export JSON & CSV artifacts
    os.makedirs(eval_config.RESULTS_DIR, exist_ok=True)
    os.makedirs(eval_config.DOCS_RESULTS_DIR, exist_ok=True)

    full_results = {
        "evaluation_status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "dataset_version": eval_config.DATASET_VERSION,
        "content_safety_audit": safety_audit,
        "baseline_metrics": baseline_metrics,
        "proposed_metrics": proposed_metrics,
        "comparison_matrix": comparison_matrix
    }

    # Save JSON results
    json_path = os.path.join(eval_config.DOCS_RESULTS_DIR, "evaluation_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    # Save CSV comparison table
    csv_path = os.path.join(eval_config.DOCS_RESULTS_DIR, "comparison_table.csv")
    if comparison_matrix:
        fieldnames = list(comparison_matrix[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(comparison_matrix)

    # 6. Generate FYP Markdown Report
    report_content = EvaluationReportGenerator.generate_markdown_report(
        safety_audit=safety_audit,
        baseline_metrics=baseline_metrics,
        proposed_metrics=proposed_metrics,
        comparison_matrix=comparison_matrix
    )

    # 7. Render Comparison Bar Chart
    generate_comparison_plots(baseline_metrics, proposed_metrics)

    print("Experimental Evaluation Completed Successfully!")
    print(f"Results exported to {json_path} and {csv_path}")

    return full_results

if __name__ == "__main__":
    run_evaluation_pipeline()
