"""Extended report comparison helpers with tolerance gates."""

from __future__ import annotations

from typing import Dict


def compare_reports_with_tolerance(baseline, current, tolerance: float = 0.01) -> Dict[str, Dict[str, float | bool]]:
    """Compare report aggregate metrics and flag regressions above tolerance.

    Both report objects are expected to expose ``aggregate_scores`` mapping.
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    baseline_scores = getattr(baseline, "aggregate_scores", {})
    current_scores = getattr(current, "aggregate_scores", {})
    metric_names = sorted(set(baseline_scores) | set(current_scores))

    comparison: Dict[str, Dict[str, float | bool]] = {}
    for name in metric_names:
        base_val = baseline_scores.get(name, 0.0)
        curr_val = current_scores.get(name, 0.0)
        delta = curr_val - base_val
        regression = delta < 0 and abs(delta) > tolerance
        comparison[name] = {
            "baseline": base_val,
            "current": curr_val,
            "delta": delta,
            "regression": regression,
        }
    return comparison
