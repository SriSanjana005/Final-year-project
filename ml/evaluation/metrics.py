import math
from typing import List, Dict, Any

def compute_confidence_interval(data: List[float], confidence: float = 0.95) -> Dict[str, Any]:
    """Calculates mean, std, and margin of error / 95% CI bounds for a continuous metric."""
    n = len(data)
    if n == 0:
        return {"mean": "N/A — Insufficient data", "std": None, "ci_lower": None, "ci_upper": None, "sample_size": 0}

    mean = sum(data) / n
    if n == 1:
        return {"mean": round(mean, 2), "std": 0.0, "ci_lower": round(mean, 2), "ci_upper": round(mean, 2), "sample_size": 1}

    variance = sum((x - mean) ** 2 for x in data) / (n - 1)
    std = math.sqrt(variance)
    
    # 95% CI z-critical approximation
    z = 1.96
    margin = z * (std / math.sqrt(n))

    return {
        "mean": round(mean, 2),
        "std": round(std, 2),
        "ci_lower": round(mean - margin, 2),
        "ci_upper": round(mean + margin, 2),
        "sample_size": n
    }

def compute_strategy_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes primary evaluation metrics for a given recommendation strategy subset.
    Tracks sample sizes N explicitly and returns evidence-based measurements.
    """
    total_recs = len(records)
    if total_recs == 0:
        return {
            "total_recommendations": 0,
            "total_learners": 0,
            "view_rate": "N/A — Insufficient data",
            "completion_rate": "N/A — Insufficient data",
            "avg_subsequent_score": "N/A — Insufficient data",
            "avg_performance_change": "N/A — Insufficient data",
            "repeated_content_rate": "N/A — Insufficient data",
            "difficulty_alignment_rate": "N/A — Insufficient data"
        }

    learners = len(set(r["child_id"] for r in records))
    viewed_count = sum(1 for r in records if r["is_viewed"])
    completed_count = sum(1 for r in records if r["is_completed"])
    repeated_count = sum(1 for r in records if r["is_repeated"])
    aligned_count = sum(1 for r in records if r["is_difficulty_aligned"])

    view_rate = viewed_count / total_recs
    completion_rate = completed_count / total_recs
    repeated_rate = repeated_count / total_recs
    alignment_rate = aligned_count / total_recs

    # Extract valid subsequent quiz scores & performance changes
    subsequent_scores = [r["subsequent_score"] for r in records if r["subsequent_score"] is not None]
    perf_changes = [r["performance_change"] for r in records if r["performance_change"] is not None]

    subsequent_score_stats = compute_confidence_interval(subsequent_scores)
    perf_change_stats = compute_confidence_interval(perf_changes)

    return {
        "total_recommendations": total_recs,
        "total_learners": learners,
        "viewed_count": viewed_count,
        "completed_count": completed_count,
        "view_rate": round(view_rate * 100.0, 1),
        "completion_rate": round(completion_rate * 100.0, 1),
        "repeated_content_rate": round(repeated_rate * 100.0, 1),
        "difficulty_alignment_rate": round(alignment_rate * 100.0, 1),
        "subsequent_score_stats": subsequent_score_stats,
        "performance_change_stats": perf_change_stats
    }
