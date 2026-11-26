"""Comprehensive test suite for the LLM Request Orchestrator v1-basic."""

import os
import sys
import time
import unittest

# ---------------------------------------------------------------------------
# Path setup – ensure the v1-basic package is importable
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_v1_dir = os.path.join(os.path.dirname(_here), "v1-basic")
if _v1_dir not in sys.path:
    sys.path.insert(0, _v1_dir)

from provider import (  # noqa: E402
    CircuitOpenError,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    MockProvider,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
    ServerError,
)
from orchestrator import (  # noqa: E402
    CircuitBreaker,
    CircuitState,
    LLMOrchestrator,
    RetryPolicy,
)
from observability import (  # noqa: E402
    LoggingHook,
    MetricsCollector,
    ObservabilityHook,
    RequestTrace,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _noop_sleep(_delay: float) -> None:
    """Replacement sleep that returns immediately (avoids real delays)."""


def _make_request(**kwargs) -> LLMRequest:
    defaults = {"prompt": "Hello", "model": "test-model"}
    defaults.update(kwargs)
    return LLMRequest(**defaults)


# ---------------------------------------------------------------------------
# TestMockProvider
# ---------------------------------------------------------------------------

class TestMockProvider(unittest.TestCase):
    """Tests for MockProvider behaviour."""

    def test_success_on_first_call(self) -> None:
        provider = MockProvider()
        resp = provider.complete(_make_request())
        self.assertEqual(resp.content, "Mock response")
        self.assertEqual(provider.call_count, 1)

    def test_fails_then_succeeds(self) -> None:
        provider = MockProvider(fail_times=2, error_type=RateLimitError)
        with self.assertRaises(RateLimitError):
            provider.complete(_make_request())
        with self.assertRaises(RateLimitError):
            provider.complete(_make_request())
        resp = provider.complete(_make_request())
        self.assertEqual(resp.content, "Mock response")
        self.assertEqual(provider.call_count, 3)

    def test_custom_response_content(self) -> None:
        provider = MockProvider(response_content="Custom!")
        resp = provider.complete(_make_request())
        self.assertEqual(resp.content, "Custom!")

    def test_error_is_retryable(self) -> None:
        provider = MockProvider(fail_times=1, error_type=ServerError)
        with self.assertRaises(ServerError) as ctx:
            provider.complete(_make_request())
        self.assertTrue(ctx.exception.retryable)


# ---------------------------------------------------------------------------
# TestRetryPolicy
# ---------------------------------------------------------------------------

class TestRetryPolicy(unittest.TestCase):
    """Tests for RetryPolicy delay calculation."""

    def test_default_values(self) -> None:
        policy = RetryPolicy()
        self.assertEqual(policy.max_retries, 3)
        self.assertEqual(policy.base_delay, 1.0)
        self.assertEqual(policy.max_delay, 30.0)
        self.assertEqual(policy.backoff_multiplier, 2.0)

    def test_delay_increases_exponentially(self) -> None:
        policy = RetryPolicy(base_delay=1.0, backoff_multiplier=2.0, max_delay=100.0)
        # Delays are: base * mult^attempt + jitter.
        # Without jitter floor: attempt 0 → ~1, attempt 1 → ~2, attempt 2 → ~4
        delays = [policy.calculate_delay(a) for a in range(3)]
        # Each delay (minus max jitter) should be >= the base exponential value
        self.assertGreaterEqual(delays[0], 1.0)
        self.assertGreaterEqual(delays[1], 2.0)
        self.assertGreaterEqual(delays[2], 4.0)

    def test_delay_capped_at_max(self) -> None:
        policy = RetryPolicy(base_delay=1.0, backoff_multiplier=10.0, max_delay=5.0)
        delay = policy.calculate_delay(5)  # 1 * 10^5 = 100_000 → capped to 5
        # delay = min(100000, 5) + jitter ∈ [0, 1) → max ~6
        self.assertLessEqual(delay, 5.0 + 1.0 + 0.01)

    def test_jitter_adds_randomness(self) -> None:
        policy = RetryPolicy(base_delay=1.0, backoff_multiplier=1.0, max_delay=100.0)
        delays = {policy.calculate_delay(0) for _ in range(20)}
        # With jitter, not all delays should be identical
        self.assertGreater(len(delays), 1)


# ---------------------------------------------------------------------------
# TestCircuitBreaker
# ---------------------------------------------------------------------------

class TestCircuitBreaker(unittest.TestCase):
    """Tests for CircuitBreaker state transitions."""

    def test_starts_closed(self) -> None:
        cb = CircuitBreaker()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.allow_request())

    def test_opens_after_threshold(self) -> None:
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.allow_request())

    def test_half_open_after_recovery_timeout(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        time.sleep(0.06)
        self.assertTrue(cb.allow_request())
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

    def test_closes_on_success_after_half_open(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        cb.record_failure()
        time.sleep(0.06)
        cb.allow_request()  # transition to HALF_OPEN
        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.failure_count, 0)

    def test_reopens_on_failure_in_half_open(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        cb.record_failure()
        time.sleep(0.06)
        cb.allow_request()  # HALF_OPEN
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)

    def test_half_open_allows_only_one_probe(self) -> None:
        """After the probe request is consumed, further HALF_OPEN calls are rejected."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
        cb.record_failure()
        time.sleep(0.06)
        self.assertTrue(cb.allow_request())   # consumes the probe slot
        self.assertFalse(cb.allow_request())  # second call must be rejected

    def test_state_change_callback(self) -> None:
        changes = []
        cb = CircuitBreaker(failure_threshold=1)
        cb.on_state_change(lambda f, t: changes.append((f, t)))
        cb.record_failure()
        self.assertEqual(changes, [("CLOSED", "OPEN")])


# ---------------------------------------------------------------------------
# TestIdempotency
# ---------------------------------------------------------------------------

class TestIdempotency(unittest.TestCase):
    """Tests for idempotency cache behaviour."""

    def test_cached_response_returned(self) -> None:
        provider = MockProvider()
        orch = LLMOrchestrator(provider=provider, sleep_fn=_noop_sleep)
        req = _make_request(idempotency_key="key-1")

        resp1 = orch.execute(req)
        resp2 = orch.execute(req)

        self.assertIs(resp1, resp2)
        self.assertEqual(provider.call_count, 1)

    def test_different_keys_are_independent(self) -> None:
        provider = MockProvider()
        orch = LLMOrchestrator(provider=provider, sleep_fn=_noop_sleep)

        resp1 = orch.execute(_make_request(idempotency_key="a"))
        resp2 = orch.execute(_make_request(idempotency_key="b"))

        self.assertEqual(provider.call_count, 2)

    def test_no_key_means_no_cache(self) -> None:
        provider = MockProvider()
        orch = LLMOrchestrator(provider=provider, sleep_fn=_noop_sleep)

        orch.execute(_make_request())
        orch.execute(_make_request())

        self.assertEqual(provider.call_count, 2)

    def test_cached_response_notifies_hooks(self) -> None:
        """Idempotency cache hits should still fire observability hooks."""
        provider = MockProvider()
        metrics = MetricsCollector()
        orch = LLMOrchestrator(provider=provider, sleep_fn=_noop_sleep)
        orch.add_hook(metrics)

        req = _make_request(idempotency_key="obs-key")
        orch.execute(req)  # first call (real)
        orch.execute(req)  # second call (cached)

        # Both calls should be counted as requests
        self.assertEqual(metrics.total_requests, 2)
        self.assertEqual(metrics.successes, 2)


# ---------------------------------------------------------------------------
# TestObservability
# ---------------------------------------------------------------------------

class TestObservability(unittest.TestCase):
    """Tests for observability hooks and metrics collector."""

    def test_logging_hook_records_events(self) -> None:
        provider = MockProvider(fail_times=1, error_type=ServerError)
        logger = LoggingHook()
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=1, base_delay=0.01),
            sleep_fn=_noop_sleep,
        )
        orch.add_hook(logger)
        orch.execute(_make_request())

        # Expect: REQUEST(0), ERROR(0), REQUEST(1), RESPONSE(1)
        self.assertEqual(len(logger.logs), 4)
        self.assertIn("REQUEST", logger.logs[0])
        self.assertIn("ERROR", logger.logs[1])
        self.assertIn("REQUEST", logger.logs[2])
        self.assertIn("RESPONSE", logger.logs[3])

    def test_metrics_total_and_retries(self) -> None:
        provider = MockProvider(fail_times=2, error_type=RateLimitError)
        metrics = MetricsCollector()
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=3, base_delay=0.01),
            sleep_fn=_noop_sleep,
        )
        orch.add_hook(metrics)
        orch.execute(_make_request())

        self.assertEqual(metrics.total_requests, 1)
        self.assertEqual(metrics.successes, 1)
        self.assertEqual(metrics.failures, 2)
        self.assertEqual(metrics.retries, 2)

    def test_metrics_latency_percentile(self) -> None:
        metrics = MetricsCollector()
        metrics.latencies = [10, 20, 30, 40, 50]
        self.assertEqual(metrics.get_latency_percentile(50), 30)
        self.assertEqual(metrics.get_latency_percentile(0), 10)

    def test_metrics_error_rate(self) -> None:
        metrics = MetricsCollector()
        metrics.total_requests = 10
        metrics.failures = 3
        self.assertAlmostEqual(metrics.get_error_rate(), 0.3)

    def test_metrics_error_rate_zero_requests(self) -> None:
        metrics = MetricsCollector()
        self.assertEqual(metrics.get_error_rate(), 0.0)

    def test_metrics_latency_percentile_empty(self) -> None:
        metrics = MetricsCollector()
        self.assertEqual(metrics.get_latency_percentile(50), 0.0)

    def test_hook_exception_does_not_disrupt(self) -> None:
        """A hook that raises should not prevent the response."""

        class BadHook(ObservabilityHook):
            def on_request(self, req, att):
                raise RuntimeError("boom")

            def on_response(self, req, resp, att):
                raise RuntimeError("boom")

            def on_error(self, req, err, att):
                raise RuntimeError("boom")

        provider = MockProvider()
        orch = LLMOrchestrator(provider=provider, sleep_fn=_noop_sleep)
        orch.add_hook(BadHook())

        resp = orch.execute(_make_request())
        self.assertEqual(resp.content, "Mock response")


# ---------------------------------------------------------------------------
# TestLLMOrchestrator (integration-level)
# ---------------------------------------------------------------------------

class TestLLMOrchestrator(unittest.TestCase):
    """Integration tests for the full orchestrator stack."""

    def test_success_no_retries(self) -> None:
        provider = MockProvider()
        orch = LLMOrchestrator(provider=provider, sleep_fn=_noop_sleep)
        resp = orch.execute(_make_request())
        self.assertEqual(resp.content, "Mock response")
        self.assertEqual(provider.call_count, 1)

    def test_retries_on_transient_error(self) -> None:
        provider = MockProvider(fail_times=2, error_type=ProviderTimeoutError)
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=3, base_delay=0.01),
            sleep_fn=_noop_sleep,
        )
        resp = orch.execute(_make_request())
        self.assertEqual(resp.content, "Mock response")
        self.assertEqual(provider.call_count, 3)

    def test_raises_after_exhausted_retries(self) -> None:
        provider = MockProvider(fail_times=100, error_type=ServerError)
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=2, base_delay=0.01),
            sleep_fn=_noop_sleep,
        )
        with self.assertRaises(ServerError):
            orch.execute(_make_request())
        # 1 initial + 2 retries = 3 calls
        self.assertEqual(provider.call_count, 3)

    def test_non_retryable_error_not_retried(self) -> None:
        class AuthError(ProviderError):
            def __init__(self):
                super().__init__("Unauthorized", retryable=False)

        class AuthFailProvider(LLMProvider):
            def __init__(self):
                self.call_count = 0

            def complete(self, request):
                self.call_count += 1
                raise AuthError()

        provider = AuthFailProvider()
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=3),
            sleep_fn=_noop_sleep,
        )
        with self.assertRaises(ProviderError):
            orch.execute(_make_request())
        self.assertEqual(provider.call_count, 1)

    def test_circuit_breaker_opens_and_rejects(self) -> None:
        provider = MockProvider(fail_times=100, error_type=ServerError)
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=0),
            circuit_breaker=breaker,
            sleep_fn=_noop_sleep,
        )
        # Trigger 2 failures to open the breaker
        for _ in range(2):
            with self.assertRaises(ServerError):
                orch.execute(_make_request())

        # Next call should be rejected by the circuit breaker
        with self.assertRaises(CircuitOpenError):
            orch.execute(_make_request())

    def test_circuit_breaker_recovers(self) -> None:
        provider = MockProvider(fail_times=2, error_type=ServerError)
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.05)
        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=0),
            circuit_breaker=breaker,
            sleep_fn=_noop_sleep,
        )
        # Open the breaker
        for _ in range(2):
            with self.assertRaises(ServerError):
                orch.execute(_make_request())
        self.assertEqual(breaker.state, CircuitState.OPEN)

        # Wait for recovery, then succeed (provider has exhausted failures)
        time.sleep(0.06)
        resp = orch.execute(_make_request())
        self.assertEqual(resp.content, "Mock response")
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    def test_request_trace_dataclass(self) -> None:
        trace = RequestTrace(
            request_id="trace-1",
            request=_make_request(),
            attempts=2,
            total_latency_ms=150.0,
            errors=["ServerError"],
            final_status="success",
        )
        self.assertEqual(trace.request_id, "trace-1")
        self.assertEqual(trace.attempts, 2)
        self.assertFalse(trace.from_cache)

    def test_circuit_breaker_state_change_with_metrics(self) -> None:
        provider = MockProvider(fail_times=100, error_type=ServerError)
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        metrics = MetricsCollector()
        breaker.on_state_change(metrics.record_circuit_state_change)

        orch = LLMOrchestrator(
            provider=provider,
            retry_policy=RetryPolicy(max_retries=0),
            circuit_breaker=breaker,
            sleep_fn=_noop_sleep,
        )
        orch.add_hook(metrics)

        for _ in range(2):
            try:
                orch.execute(_make_request())
            except ServerError:
                pass

        self.assertEqual(len(metrics.circuit_state_changes), 1)
        self.assertEqual(metrics.circuit_state_changes[0][0], "CLOSED")
        self.assertEqual(metrics.circuit_state_changes[0][1], "OPEN")


if __name__ == "__main__":
    unittest.main()
