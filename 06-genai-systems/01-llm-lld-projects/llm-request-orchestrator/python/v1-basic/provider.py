"""LLM Provider abstraction, data models, and error hierarchy."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict
import time


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LLMRequest:
    """Immutable value object representing a request to an LLM provider."""

    prompt: str
    model: str = "default-model"
    temperature: float = 0.7
    max_tokens: int = 256
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class LLMResponse:
    """Immutable value object representing a response from an LLM provider."""

    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------

class ProviderError(Exception):
    """Base exception for LLM provider errors.

    Attributes:
        retryable: Whether the caller should retry the request.
    """

    def __init__(self, message: str = "", retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class RateLimitError(ProviderError):
    """Provider rejected the request due to rate limiting."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, retryable=True)


class ProviderTimeoutError(ProviderError):
    """Provider call timed out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, retryable=True)


class ServerError(ProviderError):
    """Provider returned a server-side error (5xx equivalent)."""

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message, retryable=True)


class CircuitOpenError(Exception):
    """Raised when the circuit breaker is in the OPEN state."""

    def __init__(self, message: str = "Circuit breaker is open") -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Send *request* to the model and return the response.

        Raises:
            ProviderError: On retryable or non-retryable failures.
        """


# ---------------------------------------------------------------------------
# Mock provider for testing
# ---------------------------------------------------------------------------

class MockProvider(LLMProvider):
    """Provider that fails a configurable number of times then succeeds.

    Args:
        fail_times: Number of consecutive failures before succeeding.
        error_type: Exception class to raise on failure.
        response_content: Content returned on success.
    """

    def __init__(
        self,
        fail_times: int = 0,
        error_type: type = ServerError,
        response_content: str = "Mock response",
    ) -> None:
        self.fail_times = fail_times
        self.error_type = error_type
        self.response_content = response_content
        self.call_count: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.call_count += 1
        if self.call_count <= self.fail_times:
            raise self.error_type()

        start = time.monotonic()
        # Simulate minimal work
        latency = (time.monotonic() - start) * 1000
        return LLMResponse(
            content=self.response_content,
            model=request.model,
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": 10,
                "total_tokens": len(request.prompt.split()) + 10,
            },
            latency_ms=latency,
        )
