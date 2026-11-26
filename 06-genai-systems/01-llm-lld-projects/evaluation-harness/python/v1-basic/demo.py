"""
LLM Evaluation Harness demo — v1 basic.

Walks through the full evaluation workflow:
    1. Create test cases and build a suite
    2. Configure metrics
    3. Run evaluation with a stub model adapter
    4. Display per-case and aggregate results
    5. Compare two reports for regression detection

Run:
    python demo.py
"""

from metrics import (
    CustomMetric,
    ExactMatchMetric,
    KeywordPresenceMetric,
    LengthComplianceMetric,
    NGramOverlapMetric,
)
from model_adapter import EchoAdapter, StaticAdapter
from runner import EvaluationRunner
from test_case import TestCase, TestSuite


def main() -> None:
    """Main entry point — demonstrates each stage of the evaluation harness."""

    print("=" * 60)
    print("LLM EVALUATION HARNESS DEMO (v1-basic)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Build a test suite
    # ------------------------------------------------------------------
    print("\n--- Building Test Suite ---")
    suite = TestSuite(name="demo-suite-v1")
    suite.add_case(TestCase(
        input_text="What is RAG?",
        expected_output="RAG combines retrieval with generation.",
        tags=["definition", "short"],
    ))
    suite.add_case(TestCase(
        input_text="Explain chunking.",
        expected_output="Chunking splits documents into smaller pieces.",
        tags=["definition", "short"],
    ))
    suite.add_case(TestCase(
        input_text="List three vector databases.",
        expected_output="FAISS, Pinecone, and Weaviate are popular vector databases.",
        tags=["listing"],
    ))
    print(f"  Suite '{suite.name}' has {suite.size()} cases")
    print(f"  Cases tagged 'definition': {len(suite.filter_by_tag('definition'))}")

    # ------------------------------------------------------------------
    # 2. Configure metrics
    # ------------------------------------------------------------------
    print("\n--- Configuring Metrics ---")
    metrics = [
        ExactMatchMetric(case_sensitive=False),
        NGramOverlapMetric(n=1),
        KeywordPresenceMetric(keywords=["RAG", "chunking", "vector"]),
        LengthComplianceMetric(min_length=5, max_length=200),
        CustomMetric("word_count_check", lambda exp, act: min(
            1.0, len(act.split()) / max(len(exp.split()), 1)
        )),
    ]
    for m in metrics:
        print(f"  Metric: {m.name}")

    # ------------------------------------------------------------------
    # 3. Evaluate with EchoAdapter (returns input as output)
    # ------------------------------------------------------------------
    print("\n--- Evaluation with EchoAdapter ---")
    runner = EvaluationRunner(adapter=EchoAdapter(), metrics=metrics)
    echo_report = runner.evaluate_suite(suite, pass_threshold=0.4)
    for r in echo_report.results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] case={r.case_id[:8]}... "
              f"scores={{{', '.join(f'{k}={v:.2f}' for k, v in r.scores.items())}}}")
    print(f"  Pass rate: {echo_report.pass_rate:.1%}")
    print(f"  Aggregates: {{{', '.join(f'{k}={v:.2f}' for k, v in echo_report.aggregate_scores.items())}}}")

    # ------------------------------------------------------------------
    # 4. Evaluate with StaticAdapter (always returns fixed string)
    # ------------------------------------------------------------------
    print("\n--- Evaluation with StaticAdapter ---")
    static_runner = EvaluationRunner(
        adapter=StaticAdapter(response="I don't know."),
        metrics=metrics,
    )
    static_report = static_runner.evaluate_suite(suite, pass_threshold=0.4)
    for r in static_report.results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] case={r.case_id[:8]}... "
              f"scores={{{', '.join(f'{k}={v:.2f}' for k, v in r.scores.items())}}}")
    print(f"  Pass rate: {static_report.pass_rate:.1%}")

    # ------------------------------------------------------------------
    # 5. Compare reports (regression detection)
    # ------------------------------------------------------------------
    print("\n--- Regression Comparison (echo vs static) ---")
    comparison = EvaluationRunner.compare_reports(echo_report, static_report)
    for metric_name, details in comparison.items():
        delta = details["delta"]
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "="
        print(f"  {metric_name}: {details['baseline']:.2f} → "
              f"{details['current']:.2f} ({arrow} {delta:+.2f})")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
