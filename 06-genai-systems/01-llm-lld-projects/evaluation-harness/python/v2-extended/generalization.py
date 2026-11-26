"""Slice-aware generalization evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Callable, Dict, List, Optional


ScoreFn = Callable[[str, str], float]


def _default_score(expected: str, actual: str) -> float:
    return 1.0 if expected.strip().lower() == actual.strip().lower() else 0.0


@dataclass
class GeneralizationSlice:
    """Evaluation slice for a specific cohort or time window."""

    name: str
    expected_outputs: List[str]
    actual_outputs: List[str]
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class GeneralizationSliceResult:
    """Aggregated result for one slice."""

    slice_name: str
    sample_count: int
    mean_score: float
    pass_rate: float


@dataclass
class GeneralizationReport:
    """Full report across all evaluation slices."""

    slice_results: List[GeneralizationSliceResult]
    overall_mean_score: float
    worst_slice_name: Optional[str]
    breached_slices: List[str]


class TemporalSliceEvaluator:
    """Computes generalization quality across temporal or cohort slices."""

    def __init__(self, score_fn: ScoreFn | None = None, pass_threshold: float = 0.5) -> None:
        self.score_fn = score_fn or _default_score
        self.pass_threshold = pass_threshold

    def evaluate(self, slices: List[GeneralizationSlice]) -> GeneralizationReport:
        """Return aggregate generalization report for all slices."""
        if not slices:
            return GeneralizationReport([], 0.0, None, [])

        slice_results: List[GeneralizationSliceResult] = []
        for slc in slices:
            if len(slc.expected_outputs) != len(slc.actual_outputs):
                raise ValueError(f"Slice '{slc.name}' has mismatched expected/actual lengths")
            if not slc.expected_outputs:
                slice_results.append(
                    GeneralizationSliceResult(slc.name, 0, 0.0, 0.0)
                )
                continue

            scores = [
                self.score_fn(expected, actual)
                for expected, actual in zip(slc.expected_outputs, slc.actual_outputs)
            ]
            pass_rate = sum(1 for s in scores if s >= self.pass_threshold) / len(scores)
            slice_results.append(
                GeneralizationSliceResult(
                    slice_name=slc.name,
                    sample_count=len(scores),
                    mean_score=mean(scores),
                    pass_rate=pass_rate,
                )
            )

        overall_mean = mean(sr.mean_score for sr in slice_results) if slice_results else 0.0
        worst_slice = min(slice_results, key=lambda sr: sr.mean_score) if slice_results else None
        breached = [sr.slice_name for sr in slice_results if sr.mean_score < self.pass_threshold]
        return GeneralizationReport(
            slice_results=slice_results,
            overall_mean_score=overall_mean,
            worst_slice_name=worst_slice.slice_name if worst_slice else None,
            breached_slices=breached,
        )
