"""Tests for evaluation harness v2 generalization/drift utilities."""

import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "v2-extended",
    ),
)


class TestTemporalSliceEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        from generalization import GeneralizationSlice, TemporalSliceEvaluator

        self.GeneralizationSlice = GeneralizationSlice
        self.TemporalSliceEvaluator = TemporalSliceEvaluator

    def test_evaluate_slices(self) -> None:
        evaluator = self.TemporalSliceEvaluator(pass_threshold=0.5)
        slices = [
            self.GeneralizationSlice("s1", ["a", "b"], ["a", "x"]),
            self.GeneralizationSlice("s2", ["a"], ["a"]),
        ]
        report = evaluator.evaluate(slices)
        self.assertAlmostEqual(report.overall_mean_score, 0.75)
        self.assertEqual(report.worst_slice_name, "s1")

    def test_mismatched_lengths_raise(self) -> None:
        evaluator = self.TemporalSliceEvaluator()
        slices = [self.GeneralizationSlice("bad", ["a"], ["a", "b"])]
        with self.assertRaises(ValueError):
            evaluator.evaluate(slices)


class TestDriftDetector(unittest.TestCase):
    def setUp(self) -> None:
        from drift import DriftDetector

        self.DriftDetector = DriftDetector

    def test_drift_severity(self) -> None:
        detector = self.DriftDetector(warning_delta=0.02, critical_delta=0.05)
        stable = detector.compute(0.8, 0.79)
        warning = detector.compute(0.8, 0.77)
        critical = detector.compute(0.8, 0.70)
        self.assertEqual(stable.severity, "stable")
        self.assertEqual(warning.severity, "warning")
        self.assertEqual(critical.severity, "critical")


class TestReportComparisonWithTolerance(unittest.TestCase):
    def test_compare_reports_with_tolerance(self) -> None:
        from runner_v2 import compare_reports_with_tolerance

        class Report:
            def __init__(self, aggregate_scores):
                self.aggregate_scores = aggregate_scores

        baseline = Report({"m1": 0.90})
        current = Report({"m1": 0.895, "m2": 1.0})
        result = compare_reports_with_tolerance(baseline, current, tolerance=0.01)
        self.assertFalse(result["m1"]["regression"])
        self.assertIn("m2", result)


if __name__ == "__main__":
    unittest.main()
