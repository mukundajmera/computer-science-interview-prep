# LLM Evaluation Harness

## Problem Statement

Design an evaluation harness that runs LLM outputs against a suite of test cases and scores them using pluggable metrics. The system should support multiple scoring strategies (exact match, n-gram overlap, keyword presence, length compliance, custom scorers), aggregate results into reports with per-case and summary-level scores, and enable regression detection by comparing evaluation runs over time.

---

## Functional Requirements

1. **Test Case Definition**: Define test cases with an input prompt, expected output, tags for categorisation, and arbitrary metadata
2. **Test Suite Management**: Group test cases into named suites; filter by tag to run subsets
3. **Model Adapter Abstraction**: Plug in any LLM (or stub) behind a uniform `generate(input_text) → str` interface
4. **Multiple Metrics**: Score each output with one or more metrics — exact match, n-gram overlap, keyword presence, length compliance, and user-supplied custom scorers
5. **Per-Case Results**: Record input, expected output, actual output, per-metric scores, pass/fail status, and latency for every test case
6. **Aggregate Reports**: Produce a report with mean scores per metric, overall pass rate, total duration, and timestamp
7. **Batch Evaluation**: Evaluate an entire suite in one call, applying a configurable pass threshold
8. **Regression Detection**: Compare a current report against a baseline and surface metrics that have degraded

---

## Non-Functional Requirements

1. **Extensibility**: Adding a new metric must not require changes to the runner or report classes (Open/Closed Principle)
2. **Statelessness**: The runner itself holds no mutable state between evaluations — all state lives in reports
3. **Performance**: Metric computation should be O(n) in output length for each metric
4. **Testability**: Every component must be independently unit-testable with deterministic stubs
5. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively

---

## Constraints & Assumptions

- LLM calls are abstracted behind `ModelAdapter`; the system does **not** call real APIs (stdlib only)
- Inputs and expected outputs are plain UTF-8 strings
- Test case IDs are UUID-based and globally unique
- Metric scores are normalised to `[0.0, 1.0]`
- N-gram overlap uses simple whitespace tokenisation — not a full NLP tokeniser
- Timing uses `time.perf_counter` for sub-millisecond precision
- The harness is single-threaded; concurrent evaluation is out of scope for v1

---

## Sample Interactions

```
1. Caller creates TestCase(input_text="Summarise X", expected_output="X is …", tags=["summarisation"])
2. Caller builds a TestSuite(name="summarisation-v1") and adds cases
3. Caller instantiates a ModelAdapter (e.g. EchoAdapter for testing)
4. Caller chooses metrics: [ExactMatchMetric(), NGramOverlapMetric(n=2), KeywordPresenceMetric(keywords=["X"])]
5. EvaluationRunner(adapter, metrics).evaluate_suite(suite, pass_threshold=0.6) → EvaluationReport
6. Report contains per-case EvaluationResults and aggregate scores
7. Caller compares two reports: runner.compare_reports(baseline, current) → Dict of regressions
```

---

## Clarifying Questions to Ask

1. "What constitutes a 'pass' — all metrics above threshold, or the average?"
2. "Should n-gram overlap be precision, recall, or F1?"
3. "Do we need weighted metrics or are all metrics equally important?"
4. "Should the harness support async / streaming model outputs?"
5. "Is there a maximum test suite size we should optimise for?"
6. "Should regression detection flag any decrease, or only decreases beyond a tolerance?"
7. "Do we need to persist reports, or is in-memory comparison sufficient?"
8. "How should the harness handle model adapter errors (timeouts, exceptions)?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| TestCase | Single evaluation example with input, expected output, and tags |
| TestSuite | Named collection of test cases with filtering support |
| ModelAdapter | Abstract interface for generating LLM output from a prompt |
| Metric | Abstract scoring strategy producing a 0–1 score |
| EvaluationResult | Per-case record of scores, pass/fail, and latency |
| EvaluationReport | Aggregate report across all cases in a suite |
| EvaluationRunner | Orchestrator that drives the evaluation loop |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core metrics, model adapter stubs, test suite management, runner with reports, regression comparison |
| v2-extended | Generalization slice evaluation, drift severity signals, tolerance-aware regression comparison |
| v3-optimized | Async evaluation, streaming metric computation, persistent report store, dashboard-ready output |

---

## Related Topics

- [LLM Evaluation Concepts](../../00-concepts/llm-evaluation/) — foundational theory on evaluation methodology
- [Safety Evaluation Concepts](../../00-concepts/safety-eval/) — safety-specific evaluation strategies
- [LLM Evaluation & Safety Platform (HLD)](../../02-llm-hld-projects/llm-evaluation-safety-platform/) — system-level design that consumes an evaluation harness
- [Monitoring & Observability](../../../03-hld-concepts/monitoring-observability/) — classical monitoring parallels for model quality tracking

---

## v2-Extended Scope (Implemented)

The v2 track adds production-oriented generalization and drift diagnostics:

- `TemporalSliceEvaluator.evaluate(...)` for slice-aware quality analysis
- `DriftDetector.compute(...)` for baseline-vs-current drift severity
- `compare_reports_with_tolerance(...)` for regression gating with tolerance
- Types: `GeneralizationSlice`, `GeneralizationReport`, `DriftSignal`

Code paths:

- `python/v2-extended/generalization.py`
- `python/v2-extended/drift.py`
- `python/v2-extended/runner_v2.py`
- `python/tests/test_evaluation_harness_v2.py`
