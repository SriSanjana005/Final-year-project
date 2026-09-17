# Experimental Evaluation & Recommendation Strategy Report
**Generated Date**: `2026-09-17 19:34:24 UTC` | **Dataset Version**: `1.0.0` | **Random Seed**: `42`

---

## 1. Content Safety & Integrity Audit
Verifies that recommendations originate strictly from active topics, published content, and admin-approved resources:

- **Total Recommendations Audited**: `2`
- **Admin-Approved & Published Content**: `2` ($100.0\%$)
- **Invalid / Bypassed Recommendations**: `0` ($0.0\%$)
- **Integrity Audit Status**: `PASSED`

## 2. Recommendation Strategy Comparison Matrix
Neutral side-by-side presentation of actual recorded metrics for Rule-Based Baseline vs Transformer + PPO System:

| Metric Name | Rule-Based Baseline | Transformer + PPO System | Measurement Unit |
|---|---|---|---|
| **Recommendations Generated** | `2` | `0` | Count |
| **Learners Represented** | `1` | `0` | Count |
| **Recommendation View Rate** | `0.0%` | `N/A — Insufficient data` | % |
| **Recommendation Completion Rate** | `0.0%` | `N/A — Insufficient data` | % |
| **Repeated Content Rate** | `50.0%` | `N/A — Insufficient data` | % |
| **Difficulty Alignment Rate** | `100.0%` | `N/A — Insufficient data` | % |
| **Avg Subsequent Quiz Score** | `N/A — Insufficient data` | `None` | % |
| **Avg Performance Change (Score Diff)** | `N/A — Insufficient data` | `None` | Percentage Points |

## 3. Rule-Based Baseline Evaluation
- **Recommendations**: `2`
- **Learners**: `1`
- **View Rate**: `0.0%`
- **Completion Rate**: `0.0%`
- **Repeated Content Rate**: `50.0%`
- **Difficulty Alignment Rate**: `100.0%`

## 4. Transformer + PPO Proposed Evaluation
- **Recommendations**: `0`
- **Learners**: `0`
- **View Rate**: `N/A — Insufficient data%`
- **Completion Rate**: `N/A — Insufficient data%`
- **Repeated Content Rate**: `N/A — Insufficient data%`
- **Difficulty Alignment Rate**: `N/A — Insufficient data%`

## 5. Experimental Limitations & Research Notes
1. **Observational Data Boundaries**: All metrics reflect actual database interaction records.
2. **Cold-Start Protocol**: Learners with $< 3$ completed interactions fall back to rule-based recommendations.
3. **Zero Fabrication**: Metrics update dynamically as learners interact with the live application.

---
*Report generated automatically by `ml/evaluation/report.py`.*