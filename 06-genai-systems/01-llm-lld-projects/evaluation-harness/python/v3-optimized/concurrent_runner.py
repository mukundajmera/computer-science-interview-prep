"""Async concurrent benchmark runner with dynamic semaphore rate limiting."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Dict, List, Awaitable

from dataclasses import dataclass, field

@dataclass
class AsyncEvaluationResult:
    """Per-case evaluation outcome in async environment."""
    case_id: str
    input_text: str
    expected_output: str
    actual_output: str
    scores: Dict[str, float]
    passed: bool
    duration_ms: float

class AsyncConcurrentRunner:
    """Runs test cases concurrently using an asyncio semaphore for rate limiting."""

    def __init__(self, concurrency_limit: int = 10):
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.concurrency_limit = concurrency_limit

    def set_concurrency_limit(self, limit: int) -> None:
        """Dynamically update concurrency limit (creates a new semaphore)."""
        self.concurrency_limit = limit
        self.semaphore = asyncio.Semaphore(limit)

    async def _evaluate_single(
        self,
        case: Any,
        async_generate_fn: Callable[[str], Awaitable[str]],
        metrics_fns: Dict[str, Callable[[str, str], float]],
        pass_threshold: float = 0.5
    ) -> AsyncEvaluationResult:
        async with self.semaphore:
            start = time.perf_counter()
            actual_output = await async_generate_fn(case.input_text)

            scores = {}
            for name, metric_fn in metrics_fns.items():
                scores[name] = metric_fn(case.expected_output, actual_output)

            elapsed_ms = (time.perf_counter() - start) * 1000.0

            mean_score = sum(scores.values()) / len(scores) if scores else 0.0

            return AsyncEvaluationResult(
                case_id=case.case_id,
                input_text=case.input_text,
                expected_output=case.expected_output,
                actual_output=actual_output,
                scores=scores,
                passed=mean_score >= pass_threshold,
                duration_ms=elapsed_ms
            )

    async def evaluate_suite_concurrently(
        self,
        test_cases: List[Any],
        async_generate_fn: Callable[[str], Awaitable[str]],
        metrics_fns: Dict[str, Callable[[str, str], float]],
        pass_threshold: float = 0.5
    ) -> List[AsyncEvaluationResult]:
        """Evaluate a list of test cases concurrently."""
        tasks = [
            self._evaluate_single(case, async_generate_fn, metrics_fns, pass_threshold)
            for case in test_cases
        ]

        results = await asyncio.gather(*tasks)
        return list(results)
