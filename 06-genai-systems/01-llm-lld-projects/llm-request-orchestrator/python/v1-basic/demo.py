#!/usr/bin/env python3
"""Runnable demo showing retries, circuit breaker, idempotency, and metrics."""

import sys
import os

# Ensure the v1-basic directory is on sys.path when running as a script
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from provider import (
    LLMRequest,
    MockProvider,
    RateLimitError,
    ServerError,
    CircuitOpenError,
)
from orchestrator import LLMOrchestrator, RetryPolicy, CircuitBreaker
from observability import LoggingHook, MetricsCollector


def _separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_retry_with_backoff() -> None:
    """Demonstrate retry with exponential backoff."""
    _separator("Demo 1: Retry with Exponential Backoff")

    provider = MockProvider(fail_times=2, error_type=RateLimitError)
    policy = RetryPolicy(max_retries=3, base_delay=0.01, max_delay=1.0)
    metrics = MetricsCollector()
    logger = LoggingHook()

    orchestrator = LLMOrchestrator(
        provider=provider,
        retry_policy=policy,
        sleep_fn=lambda d: None,  # skip real delays in demo
    )
    orchestrator.add_hook(metrics)
    orchestrator.add_hook(logger)

    request = LLMRequest(prompt="Explain quantum computing", model="gpt-4")
    response = orchestrator.execute(request)

    print(f"Response: {response.content}")
    print(f"Provider calls: {provider.call_count}")
    print(f"Retries: {metrics.retries}")
    print(f"Successes: {metrics.successes}")
    print("\nLog entries:")
    for log in logger.logs:
        print(f"  {log}")


def demo_idempotency() -> None:
    """Demonstrate idempotency cache returning the same response."""
    _separator("Demo 2: Idempotency Cache")

    provider = MockProvider()
    orchestrator = LLMOrchestrator(provider=provider, sleep_fn=lambda d: None)

    request = LLMRequest(
        prompt="Summarize relativity",
        model="gpt-4",
        idempotency_key="req-abc-123",
    )

    resp1 = orchestrator.execute(request)
    resp2 = orchestrator.execute(request)

    print(f"First call  – provider calls: {provider.call_count}, content: {resp1.content}")
    print(f"Second call – provider calls: {provider.call_count}, content: {resp2.content}")
    print(f"Same object? {resp1 is resp2}")


def demo_circuit_breaker() -> None:
    """Demonstrate circuit breaker opening after repeated failures."""
    _separator("Demo 3: Circuit Breaker")

    provider = MockProvider(fail_times=100, error_type=ServerError)
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    metrics = MetricsCollector()
    breaker.on_state_change(metrics.record_circuit_state_change)

    orchestrator = LLMOrchestrator(
        provider=provider,
        retry_policy=RetryPolicy(max_retries=0),
        circuit_breaker=breaker,
        sleep_fn=lambda d: None,
    )
    orchestrator.add_hook(metrics)

    for i in range(5):
        try:
            orchestrator.execute(LLMRequest(prompt=f"Request {i}"))
        except (ServerError, CircuitOpenError) as exc:
            print(f"Request {i}: {type(exc).__name__} – breaker state: {breaker.state.value}")

    print(f"\nCircuit state changes: {metrics.circuit_state_changes}")
    print(f"Error rate: {metrics.get_error_rate():.0%}")


def demo_metrics_collection() -> None:
    """Demonstrate metrics collection across multiple requests."""
    _separator("Demo 4: Metrics Collection")

    provider = MockProvider(fail_times=1, error_type=RateLimitError)
    metrics = MetricsCollector()

    orchestrator = LLMOrchestrator(
        provider=provider,
        retry_policy=RetryPolicy(max_retries=2, base_delay=0.01),
        sleep_fn=lambda d: None,
    )
    orchestrator.add_hook(metrics)

    orchestrator.execute(LLMRequest(prompt="Hello world"))

    print(f"Total requests: {metrics.total_requests}")
    print(f"Successes: {metrics.successes}")
    print(f"Failures: {metrics.failures}")
    print(f"Retries: {metrics.retries}")
    print(f"Error rate: {metrics.get_error_rate():.0%}")
    if metrics.latencies:
        print(f"p50 latency: {metrics.get_latency_percentile(50):.2f} ms")
        print(f"p99 latency: {metrics.get_latency_percentile(99):.2f} ms")


if __name__ == "__main__":
    demo_retry_with_backoff()
    demo_idempotency()
    demo_circuit_breaker()
    demo_metrics_collection()
    print("\n✅ All demos completed successfully.")
