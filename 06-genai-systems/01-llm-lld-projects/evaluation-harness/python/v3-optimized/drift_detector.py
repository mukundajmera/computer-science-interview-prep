"""Statistical drift detection using KS and PSI metrics on score distributions."""

from __future__ import annotations
import math
from typing import List, Tuple


def compute_psi(expected: List[float], actual: List[float], buckets: int = 10) -> float:
    """Compute the Population Stability Index (PSI) between two score distributions.
    Scores are assumed to be in [0.0, 1.0].
    """
    if not expected or not actual:
        return 0.0

    # Initialize bucket counts
    expected_counts = [0] * buckets
    actual_counts = [0] * buckets

    for score in expected:
        bucket = min(int(score * buckets), buckets - 1)
        expected_counts[bucket] += 1

    for score in actual:
        bucket = min(int(score * buckets), buckets - 1)
        actual_counts[bucket] += 1

    expected_len = len(expected)
    actual_len = len(actual)

    psi = 0.0
    for i in range(buckets):
        e_pct = expected_counts[i] / expected_len
        a_pct = actual_counts[i] / actual_len

        # Avoid zero division and log(0)
        e_pct = max(e_pct, 0.0001)
        a_pct = max(a_pct, 0.0001)

        psi += (a_pct - e_pct) * math.log(a_pct / e_pct)

    return psi


def compute_ks_statistic(expected: List[float], actual: List[float]) -> float:
    """Compute the two-sample Kolmogorov-Smirnov statistic.
    Measures the maximum distance between the CDFs of the two distributions.
    """
    if not expected or not actual:
        return 0.0

    expected_sorted = sorted(expected)
    actual_sorted = sorted(actual)

    n1 = len(expected_sorted)
    n2 = len(actual_sorted)

    # All unique values from both arrays
    all_values = sorted(list(set(expected_sorted + actual_sorted)))

    max_dist = 0.0
    i = 0
    j = 0

    for v in all_values:
        while i < n1 and expected_sorted[i] <= v:
            i += 1
        while j < n2 and actual_sorted[j] <= v:
            j += 1

        cdf1 = i / n1
        cdf2 = j / n2
        max_dist = max(max_dist, abs(cdf1 - cdf2))

    return max_dist

class StatisticalDriftDetector:
    """Detector that analyzes score distributions for significant drift."""

    def __init__(self, psi_threshold: float = 0.2, ks_threshold: float = 0.1) -> None:
        self.psi_threshold = psi_threshold
        self.ks_threshold = ks_threshold

    def analyze_drift(self, baseline_scores: List[float], current_scores: List[float]) -> Tuple[bool, dict]:
        """Analyze if drift occurred based on PSI and KS statistics.
        Returns a tuple of (drift_detected, metrics_dict).
        """
        psi_val = compute_psi(baseline_scores, current_scores)
        ks_val = compute_ks_statistic(baseline_scores, current_scores)

        drift_detected = psi_val > self.psi_threshold or ks_val > self.ks_threshold

        metrics = {
            "psi": psi_val,
            "ks_statistic": ks_val,
            "psi_drift": psi_val > self.psi_threshold,
            "ks_drift": ks_val > self.ks_threshold,
        }

        return drift_detected, metrics
