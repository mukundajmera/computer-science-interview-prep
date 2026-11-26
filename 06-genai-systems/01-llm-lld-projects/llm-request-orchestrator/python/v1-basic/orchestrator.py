"""LLM Request Orchestrator with retry, circuit breaker, and idempotency."""

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from provider import (
    CircuitOpenError,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ProviderError,
)
from observability import ObservabilityHook


# ---------------------------------------------------------------------------
# Retry policy
# ---------------------------------------------------------------------------

@dataclass
class RetryPolicy:
    """Configuration for retry behaviour with exponential backoff.

    Attributes:
        max_retries: Maximum number of retry attempts (0 = no retries).
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Upper-bound cap on any single delay.
        backoff_multiplier: Factor applied on each successive attempt.
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_multiplier: float = 2.0

    def calculate_delay(self, attempt: int) -> float:
        """Return the backoff delay for *attempt* (0-based), with jitter."""
        delay = self.base_delay * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay)
        jitter = random.uniform(0, 1) * self.base_delay
        return delay + jitter


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Simple consecutive-failure circuit breaker.

    States:
        CLOSED   – requests flow normally.
        OPEN     – requests are rejected immediately.
        HALF_OPEN – one probe request is allowed to test recovery.

    Args:
        failure_threshold: Consecutive failures before opening.
        recovery_timeout: Seconds to wait before probing in HALF_OPEN.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: float = 0.0
        self._half_open_probe_in_flight: bool = False
        self._state_change_callbacks: List = []

    @property
    def state(self) -> CircuitState:
        return self._state

    def allow_request(self) -> bool:
        """Return *True* if a request is allowed under the current state."""
        if self._state == CircuitState.CLOSED:
            return True
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self._transition(CircuitState.HALF_OPEN)
                self._half_open_probe_in_flight = True
                return True
            return False
        # HALF_OPEN – allow only a single probe request
        if self._half_open_probe_in_flight:
            return False
        self._half_open_probe_in_flight = True
        return True

    def record_success(self) -> None:
        """Record a successful call; close the circuit."""
        self.failure_count = 0
        self._half_open_probe_in_flight = False
        if self._state != CircuitState.CLOSED:
            self._transition(CircuitState.CLOSED)

    def record_failure(self) -> None:
        """Record a failed call; open the circuit if threshold is reached."""
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        self._half_open_probe_in_flight = False
        if self.failure_count >= self.failure_threshold:
            if self._state != CircuitState.OPEN:
                self._transition(CircuitState.OPEN)

    def on_state_change(self, callback) -> None:
        """Register a callback invoked on state transitions."""
        self._state_change_callbacks.append(callback)

    def _transition(self, new_state: CircuitState) -> None:
        old_state = self._state
        self._state = new_state
        for cb in self._state_change_callbacks:
            try:
                cb(old_state.value, new_state.value)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class LLMOrchestrator:
    """Wraps an LLMProvider with retry, idempotency, circuit breaking, and hooks.

    Args:
        provider: The underlying LLM backend.
        retry_policy: Retry configuration (defaults to sensible values).
        circuit_breaker: Circuit breaker instance (defaults to a new one).
        sleep_fn: Injectable sleep function (for testing without real delays).
    """

    def __init__(
        self,
        provider: LLMProvider,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        sleep_fn=None,
    ) -> None:
        self.provider = provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self._hooks: List[ObservabilityHook] = []
        self._idempotency_cache: Dict[str, LLMResponse] = {}
        self._sleep = sleep_fn or time.sleep

    # -- public API ---------------------------------------------------------

    def add_hook(self, hook: ObservabilityHook) -> None:
        """Register an observability hook."""
        self._hooks.append(hook)

    def execute(self, request: LLMRequest) -> LLMResponse:
        """Execute *request* through the full resilience stack.

        1. Check idempotency cache.
        2. Enter retry loop (up to max_retries + 1 total attempts).
        3. Check circuit breaker before each attempt.
        4. Call provider; on retryable error, back off and retry.
        5. Cache response if an idempotency key is present.

        Raises:
            CircuitOpenError: If the circuit breaker is OPEN.
            ProviderError: If all retries are exhausted.
        """
        # Idempotency cache check
        if request.idempotency_key and request.idempotency_key in self._idempotency_cache:
            cached_response = self._idempotency_cache[request.idempotency_key]
            self._notify_request(request, attempt=0)
            self._notify_response(request, cached_response, attempt=0)
            return cached_response

        last_error: Optional[ProviderError] = None
        max_attempts = self.retry_policy.max_retries + 1

        for attempt in range(max_attempts):
            # Circuit breaker gate
            if not self.circuit_breaker.allow_request():
                raise CircuitOpenError()

            self._notify_request(request, attempt)

            try:
                start = time.monotonic()
                response = self.provider.complete(request)
                elapsed_ms = (time.monotonic() - start) * 1000

                # Replace latency with orchestrator-measured value
                response = LLMResponse(
                    content=response.content,
                    model=response.model,
                    usage=response.usage,
                    latency_ms=elapsed_ms,
                )

                self.circuit_breaker.record_success()
                self._notify_response(request, response, attempt)

                if request.idempotency_key:
                    self._idempotency_cache[request.idempotency_key] = response

                return response

            except ProviderError as exc:
                last_error = exc
                self.circuit_breaker.record_failure()
                self._notify_error(request, exc, attempt)

                if not exc.retryable:
                    raise

                # Don't sleep after the last attempt
                if attempt < max_attempts - 1:
                    delay = self.retry_policy.calculate_delay(attempt)
                    self._sleep(delay)

        # All retries exhausted
        raise last_error  # type: ignore[misc]

    # -- hook notification helpers ------------------------------------------

    def _notify_request(self, request: LLMRequest, attempt: int) -> None:
        for hook in self._hooks:
            try:
                hook.on_request(request, attempt)
            except Exception:
                pass

    def _notify_response(
        self, request: LLMRequest, response: LLMResponse, attempt: int
    ) -> None:
        for hook in self._hooks:
            try:
                hook.on_response(request, response, attempt)
            except Exception:
                pass

    def _notify_error(
        self, request: LLMRequest, error: ProviderError, attempt: int
    ) -> None:
        for hook in self._hooks:
            try:
                hook.on_error(request, error, attempt)
            except Exception:
                pass
