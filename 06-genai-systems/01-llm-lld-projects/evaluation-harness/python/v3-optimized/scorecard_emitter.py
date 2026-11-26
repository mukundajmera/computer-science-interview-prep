"""Automated scorecard report emitter for v3-optimized harness."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List
from datetime import datetime, timezone

class ScorecardEmitter:
    """Emits automated scorecard reports in JSON and Markdown formats."""

    @staticmethod
    def generate_json_report(
        suite_name: str,
        results: List[Any],
        aggregate_scores: Dict[str, float]
    ) -> str:
        """Generate a JSON report."""
        report = {
            "suite_name": suite_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "aggregate_scores": aggregate_scores,
            "pass_rate": sum(1 for r in results if r.passed) / len(results) if results else 0.0,
            "total_cases": len(results),
            "total_duration_ms": sum(r.duration_ms for r in results) if results else 0.0,
            "results": [asdict(r) for r in results]
        }
        return json.dumps(report, indent=2)

    @staticmethod
    def generate_markdown_report(
        suite_name: str,
        results: List[Any],
        aggregate_scores: Dict[str, float]
    ) -> str:
        """Generate a Markdown report."""
        pass_rate = sum(1 for r in results if r.passed) / len(results) if results else 0.0
        total_duration = sum(r.duration_ms for r in results) if results else 0.0

        lines = [
            f"# Evaluation Scorecard: {suite_name}",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Summary",
            f"- **Pass Rate:** {pass_rate * 100:.2f}%",
            f"- **Total Cases:** {len(results)}",
            f"- **Total Duration:** {total_duration:.2f} ms",
            "",
            "### Aggregate Scores"
        ]

        for metric, score in aggregate_scores.items():
            lines.append(f"- **{metric}:** {score:.4f}")

        lines.extend([
            "",
            "## Detailed Results",
            "| Case ID | Passed | Duration (ms) | Scores |",
            "|---------|--------|---------------|--------|"
        ])

        for r in results:
            scores_str = ", ".join(f"{m}={s:.2f}" for m, s in r.scores.items())
            lines.append(f"| {r.case_id} | {'✅' if r.passed else '❌'} | {r.duration_ms:.1f} | {scores_str} |")

        return "\n".join(lines)
