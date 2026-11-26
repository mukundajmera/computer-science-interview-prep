"""Tests for evaluation harness v3 optimized components."""

import asyncio
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "..",
        "v3-optimized",
    ))
)

import pytest
from concurrent_runner import AsyncConcurrentRunner, AsyncEvaluationResult
from drift_detector import StatisticalDriftDetector, compute_psi, compute_ks_statistic

class DummyCase:
    def __init__(self, case_id: str, input_text: str, expected_output: str):
        self.case_id = case_id
        self.input_text = input_text
        self.expected_output = expected_output

async def dummy_generate(input_text: str) -> str:
    await asyncio.sleep(0.01)
    return input_text

def dummy_metric(expected: str, actual: str) -> float:
    return 1.0 if expected == actual else 0.0

def test_async_concurrent_runner_success():
    """Test the async runner completes correctly and produces expected results."""
    async def _test():
        runner = AsyncConcurrentRunner(concurrency_limit=2)
        cases = [
            DummyCase("1", "hello", "hello"),
            DummyCase("2", "world", "world"),
        ]

        results = await runner.evaluate_suite_concurrently(
            test_cases=cases,
            async_generate_fn=dummy_generate,
            metrics_fns={"exact": dummy_metric}
        )

        assert len(results) == 2
        for r in results:
            assert r.scores["exact"] == 1.0
            assert r.passed is True
            assert r.duration_ms > 0

    asyncio.run(_test())

def test_async_concurrent_runner_failure():
    """Test the async runner handles non-matching expected vs actual outputs."""
    async def _test():
        async def bad_generate(text: str) -> str:
            return "bad_output"

        runner = AsyncConcurrentRunner(concurrency_limit=5)
        cases = [
            DummyCase("1", "hello", "hello")
        ]

        results = await runner.evaluate_suite_concurrently(
            test_cases=cases,
            async_generate_fn=bad_generate,
            metrics_fns={"exact": dummy_metric}
        )

        assert len(results) == 1
        assert results[0].scores["exact"] == 0.0
        assert results[0].passed is False

    asyncio.run(_test())

def test_drift_detector_no_drift():
    """Test the drift detector when distributions are identical."""
    detector = StatisticalDriftDetector(psi_threshold=0.1, ks_threshold=0.1)
    scores1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    scores2 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    drift, stats = detector.analyze_drift(scores1, scores2)
    assert drift is False
    assert stats["psi"] < 0.1
    assert stats["ks_statistic"] < 0.1

def test_drift_detector_with_drift():
    """Test the drift detector when distributions are significantly different."""
    detector = StatisticalDriftDetector(psi_threshold=0.1, ks_threshold=0.1)
    baseline = [0.8, 0.9, 0.9, 0.8, 0.9, 1.0]
    current = [0.1, 0.2, 0.1, 0.3, 0.1, 0.2]

    drift, stats = detector.analyze_drift(baseline, current)
    assert drift is True
    assert stats["ks_statistic"] > 0.1

from scorecard_emitter import ScorecardEmitter

def test_scorecard_emitter_json():
    """Test generating a JSON scorecard report."""
    results = [
        AsyncEvaluationResult("1", "in", "out", "out", {"exact": 1.0}, True, 10.0),
        AsyncEvaluationResult("2", "in2", "out2", "bad", {"exact": 0.0}, False, 15.0)
    ]
    json_report = ScorecardEmitter.generate_json_report("test_suite", results, {"exact": 0.5})
    assert '"suite_name": "test_suite"' in json_report
    assert '"pass_rate": 0.5' in json_report
    assert '"exact": 1.0' in json_report

def test_scorecard_emitter_markdown():
    """Test generating a Markdown scorecard report."""
    results = [
        AsyncEvaluationResult("1", "in", "out", "out", {"exact": 1.0}, True, 10.0),
        AsyncEvaluationResult("2", "in2", "out2", "bad", {"exact": 0.0}, False, 15.0)
    ]
    md_report = ScorecardEmitter.generate_markdown_report("test_suite", results, {"exact": 0.5})
    assert "# Evaluation Scorecard: test_suite" in md_report
    assert "- **Pass Rate:** 50.00%" in md_report
    assert "✅" in md_report
    assert "❌" in md_report
