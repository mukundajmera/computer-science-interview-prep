"""
Evaluation runner and report module.

Provides dataclasses for evaluation results and reports, and the
:class:`EvaluationRunner` that orchestrates the eval loop: generate
output, score with each metric, aggregate into a report.

Design patterns:
    - Template Method — fixed evaluation flow with pluggable metrics
    - Strategy        — delegates scoring to injected :class:`Metric` list
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from metrics import Metric
from model_adapter import ModelAdapter
from test_case import TestCase, TestSuite


@dataclass
class EvaluationResult:
    """Per-case evaluation outcome.

    Attributes:
        case_id:         Originating test case ID.
        input_text:      The prompt sent to the model.
        expected_output: Ground-truth answer.
        actual_output:   Model-generated output.
        scores:          Metric name → score mapping.
        passed:          Whether the mean score met the pass threshold.
        duration_ms:     Wall-clock time for generation + scoring (ms).
    """

    case_id: str
    input_text: str
    expected_output: str
    actual_output: str
    scores: Dict[str, float]
    passed: bool
    duration_ms: float


@dataclass
class EvaluationReport:
    """Aggregate report for a suite evaluation run.

    Attributes:
        suite_name:       Name of the evaluated suite.
        results:          Per-case :class:`EvaluationResult` list.
        aggregate_scores: Mean score per metric across all cases.
        pass_rate:        Fraction of cases that passed.
        total_duration_ms: Sum of all case durations (ms).
        timestamp:        ISO-8601 timestamp of report creation.
    """

    suite_name: str
    results: List[EvaluationResult]
    aggregate_scores: Dict[str, float]
    pass_rate: float
    total_duration_ms: float
    timestamp: str


class EvaluationRunner:
    """Orchestrates LLM evaluation: generate, score, and aggregate.

    Args:
        adapter: :class:`ModelAdapter` used to generate outputs.
        metrics: List of :class:`Metric` instances to apply.

    Attributes:
        adapter: The injected model adapter.
        metrics: The injected list of metrics.
    """

    def __init__(self, adapter: ModelAdapter, metrics: List[Metric]) -> None:
        self.adapter = adapter
        self.metrics = metrics

    def evaluate_case(
        self, test_case: TestCase, pass_threshold: float = 0.5
    ) -> EvaluationResult:
        """Run a single test case through generation and scoring.

        Args:
            test_case:      The :class:`TestCase` to evaluate.
            pass_threshold: Minimum mean score to mark as passed.

        Returns:
            An :class:`EvaluationResult` with per-metric scores and timing.
        """
        start = time.perf_counter()
        actual_output = self.adapter.generate(test_case.input_text)
        scores: Dict[str, float] = {}
        for metric in self.metrics:
            scores[metric.name] = metric.score(
                test_case.expected_output, actual_output
            )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        mean_score = (
            sum(scores.values()) / len(scores) if scores else 0.0
        )
        return EvaluationResult(
            case_id=test_case.case_id,
            input_text=test_case.input_text,
            expected_output=test_case.expected_output,
            actual_output=actual_output,
            scores=scores,
            passed=mean_score >= pass_threshold,
            duration_ms=elapsed_ms,
        )

    def evaluate_suite(
        self, test_suite: TestSuite, pass_threshold: float = 0.5
    ) -> EvaluationReport:
        """Evaluate all cases in a suite and produce an aggregate report.

        Args:
            test_suite:     The :class:`TestSuite` to evaluate.
            pass_threshold: Minimum mean score per case to count as passed.

        Returns:
            An :class:`EvaluationReport` with per-case results and aggregates.
        """
        results: List[EvaluationResult] = []
        for tc in test_suite.test_cases:
            results.append(self.evaluate_case(tc, pass_threshold))

        aggregate_scores = self._compute_aggregates(results)
        passed_count = sum(1 for r in results if r.passed)
        pass_rate = passed_count / len(results) if results else 0.0
        total_duration = sum(r.duration_ms for r in results)
        timestamp = datetime.now(timezone.utc).isoformat()

        return EvaluationReport(
            suite_name=test_suite.name,
            results=results,
            aggregate_scores=aggregate_scores,
            pass_rate=pass_rate,
            total_duration_ms=total_duration,
            timestamp=timestamp,
        )

    @staticmethod
    def compare_reports(
        baseline: EvaluationReport, current: EvaluationReport
    ) -> Dict[str, Dict[str, float]]:
        """Compare two reports and identify metric regressions.

        For each metric present in both reports, computes the delta
        (current − baseline).  Negative deltas indicate regressions.

        Args:
            baseline: The reference :class:`EvaluationReport`.
            current:  The new :class:`EvaluationReport` to compare.

        Returns:
            A dict mapping metric names to ``{"baseline", "current", "delta"}``.
        """
        comparison: Dict[str, Dict[str, float]] = {}
        all_metrics = set(baseline.aggregate_scores) | set(
            current.aggregate_scores
        )
        for metric_name in sorted(all_metrics):
            base_val = baseline.aggregate_scores.get(metric_name, 0.0)
            curr_val = current.aggregate_scores.get(metric_name, 0.0)
            comparison[metric_name] = {
                "baseline": base_val,
                "current": curr_val,
                "delta": curr_val - base_val,
            }
        return comparison

    @staticmethod
    def _compute_aggregates(
        results: List[EvaluationResult],
    ) -> Dict[str, float]:
        """Compute mean score per metric across all results.

        Args:
            results: List of :class:`EvaluationResult` instances.

        Returns:
            Dict mapping metric names to their mean scores.
        """
        if not results:
            return {}
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for result in results:
            for name, val in result.scores.items():
                totals[name] = totals.get(name, 0.0) + val
                counts[name] = counts.get(name, 0) + 1
        return {name: totals[name] / counts[name] for name in totals}
