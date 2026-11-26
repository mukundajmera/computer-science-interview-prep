"""Demo for slice-based evaluation and drift detection."""

from __future__ import annotations

from drift import DriftDetector
from generalization import GeneralizationSlice, TemporalSliceEvaluator


class Report:
    def __init__(self, aggregate_scores):
        self.aggregate_scores = aggregate_scores


def main() -> None:
    evaluator = TemporalSliceEvaluator(pass_threshold=0.6)
    slices = [
        GeneralizationSlice(
            name="recent_week",
            expected_outputs=["safe", "safe", "block"],
            actual_outputs=["safe", "flag", "block"],
        ),
        GeneralizationSlice(
            name="older_week",
            expected_outputs=["safe", "block"],
            actual_outputs=["safe", "safe"],
        ),
    ]
    report = evaluator.evaluate(slices)
    print("overall_mean_score=", round(report.overall_mean_score, 3))
    print("worst_slice=", report.worst_slice_name)
    print("breached=", report.breached_slices)

    detector = DriftDetector()
    drift = detector.compute(0.86, 0.80, metric_name="precision")
    print("drift=", drift)

    baseline = Report({"exact_match": 0.86})
    current = Report({"exact_match": 0.80})
    from runner_v2 import compare_reports_with_tolerance

    print(compare_reports_with_tolerance(baseline, current, tolerance=0.01))


if __name__ == "__main__":
    main()
