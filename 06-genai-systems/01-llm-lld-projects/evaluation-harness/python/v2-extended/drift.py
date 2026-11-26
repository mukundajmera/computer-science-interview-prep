"""Drift signal calculations for evaluation report comparisons."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftSignal:
    """Represents metric drift between baseline and current values."""

    metric_name: str
    baseline_value: float
    current_value: float
    delta: float
    relative_delta: float
    severity: str


class DriftDetector:
    """Computes drift magnitude and classifies severity."""

    def __init__(self, warning_delta: float = 0.02, critical_delta: float = 0.05) -> None:
        if warning_delta < 0 or critical_delta < 0:
            raise ValueError("Delta thresholds must be non-negative")
        if warning_delta > critical_delta:
            raise ValueError("warning_delta must be <= critical_delta")
        self.warning_delta = warning_delta
        self.critical_delta = critical_delta

    def compute(self, baseline_value: float, current_value: float, metric_name: str = "score") -> DriftSignal:
        """Compute drift from baseline to current value."""
        delta = current_value - baseline_value
        abs_delta = abs(delta)
        relative = 0.0 if baseline_value == 0 else delta / baseline_value
        if abs_delta >= self.critical_delta:
            severity = "critical"
        elif abs_delta >= self.warning_delta:
            severity = "warning"
        else:
            severity = "stable"
        return DriftSignal(metric_name, baseline_value, current_value, delta, relative, severity)
