import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.evaluation.config import eval_config

def generate_comparison_plots(baseline_metrics: dict, proposed_metrics: dict):
    """
    Generates side-by-side strategy comparison bar chart PNG figure.
    Exports figure to docs/results/strategy_comparison.png.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Notice: matplotlib not available for comparison plot rendering.")
        return False

    metrics_list = ["View Rate", "Completion Rate", "Repeated Rate", "Difficulty Align"]
    
    rb_vals = [
        baseline_metrics.get("view_rate", 0) if isinstance(baseline_metrics.get("view_rate"), (int, float)) else 0,
        baseline_metrics.get("completion_rate", 0) if isinstance(baseline_metrics.get("completion_rate"), (int, float)) else 0,
        baseline_metrics.get("repeated_content_rate", 0) if isinstance(baseline_metrics.get("repeated_content_rate"), (int, float)) else 0,
        baseline_metrics.get("difficulty_alignment_rate", 0) if isinstance(baseline_metrics.get("difficulty_alignment_rate"), (int, float)) else 0,
    ]

    pr_vals = [
        proposed_metrics.get("view_rate", 0) if isinstance(proposed_metrics.get("view_rate"), (int, float)) else 0,
        proposed_metrics.get("completion_rate", 0) if isinstance(proposed_metrics.get("completion_rate"), (int, float)) else 0,
        proposed_metrics.get("repeated_content_rate", 0) if isinstance(proposed_metrics.get("repeated_content_rate"), (int, float)) else 0,
        proposed_metrics.get("difficulty_alignment_rate", 0) if isinstance(proposed_metrics.get("difficulty_alignment_rate"), (int, float)) else 0,
    ]

    x = range(len(metrics_list))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5))
    rects1 = ax.bar([i - width/2 for i in x], rb_vals, width, label="Rule-Based Baseline", color="#64748B")
    rects2 = ax.bar([i + width/2 for i in x], pr_vals, width, label="Transformer + PPO", color="#2563EB")

    ax.set_ylabel("Percentage (%)")
    ax.set_title("Recommendation Strategy Performance Metrics Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_list)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()

    for rects in [rects1, rects2]:
        for bar in rects:
            h = bar.get_height()
            if h > 0:
                ax.annotate(f"{h:.1f}%",
                            xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    os.makedirs(eval_config.RESULTS_DIR, exist_ok=True)
    os.makedirs(eval_config.DOCS_RESULTS_DIR, exist_ok=True)

    plt.savefig(os.path.join(eval_config.RESULTS_DIR, "strategy_comparison.png"), dpi=150)
    plt.savefig(os.path.join(eval_config.DOCS_RESULTS_DIR, "strategy_comparison.png"), dpi=150)
    plt.close()
    print("Generated strategy_comparison.png")
    return True
