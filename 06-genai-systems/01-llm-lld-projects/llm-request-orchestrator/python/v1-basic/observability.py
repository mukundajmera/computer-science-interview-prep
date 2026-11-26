"""Observability hooks, metrics collector, and request tracing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time


# ---------------------------------------------------------------------------
# Abstract hook
# ---------------------------------------------------------------------------

class ObservabilityHook(ABC):
    """Abstract lifecycle observer for orchestrated LLM requests."""

    @abstractmethod
    def on_request(self, request, attempt: int) -> None:
        """Called before each provider call attempt."""

    @abstractmethod
    def on_response(self, request, response, attempt: int) -> None:
        """Called after a successful provider call."""

    @abstractmethod
    def on_error(self, request, error: Exception, attempt: int) -> None:
        """Called after a failed provider call."""


# ---------------------------------------------------------------------------
# Logging hook
# ---------------------------------------------------------------------------

class LoggingHook(ObservabilityHook):
    """Hook that appends structured log messages to an in-memory list.

    Useful for testing and debugging without external dependencies.
    """

    def __init__(self) -> None:
        self.logs: List[str] = []

    def on_request(self, request, attempt: int) -> None:
        self.logs.append(
            f"REQUEST  attempt={attempt} model={request.model} "
            f"prompt={request.prompt[:50]!r}"
        )

    def on_response(self, request, response, attempt: int) -> None:
        self.logs.append(
            f"RESPONSE attempt={attempt} model={response.model} "
            f"latency_ms={response.latency_ms:.2f}"
        )

    def on_error(self, request, error: Exception, attempt: int) -> None:
        self.logs.append(
            f"ERROR    attempt={attempt} error={type(error).__name__}: {error}"
        )


# ---------------------------------------------------------------------------
# Metrics collector
# ---------------------------------------------------------------------------

class MetricsCollector(ObservabilityHook):
    """Concrete hook that aggregates operational metrics.

    Tracks total requests, successes, failures, retries, latencies,
    and circuit-breaker state transitions.
    """

    def __init__(self) -> None:
        self.total_requests: int = 0
        self.successes: int = 0
        self.failures: int = 0
        self.retries: int = 0
        self.latencies: List[float] = []
        self.circuit_state_changes: List[Tuple[str, str, float]] = []

    # -- hook callbacks -----------------------------------------------------

    def on_request(self, request, attempt: int) -> None:
        if attempt == 0:
            self.total_requests += 1
        else:
            self.retries += 1

    def on_response(self, request, response, attempt: int) -> None:
        self.successes += 1
        self.latencies.append(response.latency_ms)

    def on_error(self, request, error: Exception, attempt: int) -> None:
        self.failures += 1

    # -- circuit breaker observation ----------------------------------------

    def record_circuit_state_change(
        self, from_state: str, to_state: str
    ) -> None:
        """Record a circuit breaker state transition."""
        self.circuit_state_changes.append(
            (from_state, to_state, time.monotonic())
        )

    # -- query helpers ------------------------------------------------------

    def get_latency_percentile(self, p: float) -> float:
        """Return the *p*-th percentile (0–100) of recorded latencies.

        Returns 0.0 if no latencies have been recorded.
        """
        if not self.latencies:
            return 0.0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * p / 100)
        idx = min(idx, len(sorted_lat) - 1)
        return sorted_lat[idx]

    def get_error_rate(self) -> float:
        """Return the ratio of failures to total requests (0.0–1.0)."""
        if self.total_requests == 0:
            return 0.0
        return self.failures / self.total_requests


# ---------------------------------------------------------------------------
# Request trace
# ---------------------------------------------------------------------------

@dataclass
class RequestTrace:
    """Captures the full lifecycle of a single orchestrated request."""

    request_id: str
    request: object
    response: Optional[object] = None
    attempts: int = 0
    total_latency_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    from_cache: bool = False
    final_status: str = "pending"
