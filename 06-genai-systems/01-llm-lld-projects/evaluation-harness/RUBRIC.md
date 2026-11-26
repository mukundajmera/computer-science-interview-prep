# Evaluation Harness — Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Evaluation Harness project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies evaluation criteria (exact match, BLEU/ROUGE heuristic, semantic similarity), benchmark dataset schemas, and aggregation. |
| Domain model quality | 25% | Clean abstraction of `MetricEvaluator`, `BenchmarkDataset`, `EvaluationResult`, and `EvaluationHarness`. |
| Pipeline correctness | 25% | Accurate computation of precision, recall, F1, exact match, and handling of empty or edge-case outputs. |
| Reporting & Summary | 20% | Generates structured summary reports with breakdown by test case and overall pass/fail thresholds. |
| Extensibility & Tests | 15% | Uses Strategy pattern for new evaluation metrics, pluggable judge interfaces, zero third-party deps. |

## Performance bands

- `1/5`: Monolithic script doing simple string comparison without metric abstractions or report generation.
- `3/5`: Implements metric evaluator classes, but lacks clean aggregation, threshold gating, or robust edge-case handling.
- `5/5`: Extensible Strategy pattern for evaluators, comprehensive reporting with statistical summaries, threshold assertion runner.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
