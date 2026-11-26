"""Demo for v3-optimized components."""

import asyncio
from typing import List

from concurrent_runner import AsyncConcurrentRunner
from drift_detector import StatisticalDriftDetector

class DummyCase:
    def __init__(self, case_id: str, input_text: str, expected_output: str):
        self.case_id = case_id
        self.input_text = input_text
        self.expected_output = expected_output

async def dummy_generate(input_text: str) -> str:
    await asyncio.sleep(0.01)
    return input_text

def exact_match(expected: str, actual: str) -> float:
    return 1.0 if expected == actual else 0.0

async def run_demo():
    print("Running v3-optimized demo...")

    runner = AsyncConcurrentRunner(concurrency_limit=5)
    cases = [
        DummyCase(str(i), f"input_{i}", f"input_{i}") for i in range(10)
    ]

    metrics = {"exact_match": exact_match}

    results = await runner.evaluate_suite_concurrently(
        test_cases=cases,
        async_generate_fn=dummy_generate,
        metrics_fns=metrics
    )

    print(f"Evaluated {len(results)} cases concurrently.")

    # Drift detection
    detector = StatisticalDriftDetector(psi_threshold=0.1, ks_threshold=0.1)

    # Simulate a drift scenario
    baseline_scores = [1.0] * 10
    current_scores = [0.5, 0.4, 0.5, 0.6, 0.5, 0.4, 0.5, 0.4, 0.5, 0.6]

    drift_detected, stats = detector.analyze_drift(baseline_scores, current_scores)

    print(f"Drift detected: {drift_detected}")
    print(f"Stats: {stats}")

    # Scorecard Emission
    from scorecard_emitter import ScorecardEmitter

    # Calculate dummy aggregates
    aggregates = {"exact_match": sum(r.scores["exact_match"] for r in results) / len(results)}

    json_report = ScorecardEmitter.generate_json_report("demo_suite", results, aggregates)
    md_report = ScorecardEmitter.generate_markdown_report("demo_suite", results, aggregates)

    print("\n--- JSON Report Preview ---")
    print(json_report[:200] + "...\n")
    print("--- Markdown Report Preview ---")
    print(md_report[:200] + "...\n")

if __name__ == "__main__":
    asyncio.run(run_demo())
