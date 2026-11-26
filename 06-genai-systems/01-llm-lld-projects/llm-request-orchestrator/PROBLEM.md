# LLM Request Orchestrator

## Problem Statement

Design a wrapper around an LLM provider that handles retries, exponential backoff, idempotency, circuit breaking, and observability. The orchestrator must make LLM API calls resilient to transient failures while providing full visibility into request lifecycles.

---

## Functional Requirements

1. **Wrap LLM Provider Calls**: Provide a single `execute(request)` entry point that delegates to an underlying LLM provider while adding reliability and observability layers
2. **Retry with Exponential Backoff**: Automatically retry failed requests using configurable exponential backoff with jitter to avoid thundering-herd problems
3. **Idempotency Key Support**: Accept an optional idempotency key per request; if the same key is seen again, return the cached response without calling the provider
4. **Circuit Breaker Pattern**: Track consecutive provider failures and open the circuit when a threshold is reached, immediately rejecting new requests until a recovery timeout expires and a probe succeeds
5. **Observability Hooks**: Emit structured events at each lifecycle stage — request start, response received, error encountered — so callers can attach logging, metrics, or tracing
6. **Configurable Retry Policies**: Allow callers to supply a `RetryPolicy` specifying max retries, base delay, maximum delay, and backoff multiplier
7. **Provider Abstraction**: Define an abstract `LLMProvider` interface so any backend (OpenAI, Anthropic, local model) can be plugged in without changing orchestration logic
8. **Metrics Collection**: Track total requests, successes, failures, retries, latency percentiles, and circuit breaker state transitions

---

## Non-Functional Requirements

1. **Resilience**: The system must gracefully handle transient failures (rate limits, timeouts, server errors) without losing requests that carry an idempotency key
2. **Observability**: Every request must produce a trace capturing timing, retry count, final outcome, and any errors encountered
3. **Provider-Agnostic**: Swapping from one LLM provider to another must require zero changes to orchestration or observability code
4. **Deterministic Caching**: Given the same idempotency key, the response must be identical regardless of how many times `execute` is called
5. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively
6. **Testability**: Every component (provider, circuit breaker, retry logic, hooks) must be independently unit-testable

---

## Constraints & Assumptions

- The orchestrator wraps **synchronous** provider calls in v1; async support is deferred to v2
- Idempotency cache is in-memory (`dict`); persistent storage is out of scope for v1
- Jitter is added to backoff delays using `random.uniform(0, 1) * base_delay` to decorrelate retries
- Circuit breaker uses a simple consecutive-failure counter, not a sliding window
- The circuit breaker has three states: **CLOSED** (normal), **OPEN** (rejecting), **HALF_OPEN** (probing)
- Provider errors are classified into retryable (`RateLimitError`, `TimeoutError`, `ServerError`) and non-retryable (all others)
- Observability hooks are synchronous; they must not raise exceptions that disrupt the request flow

---

## Sample Interactions

```
1. Caller creates an LLMOrchestrator with a MockProvider and a RetryPolicy(max_retries=3)
2. Caller calls orchestrator.execute(request) with a prompt
3. Provider raises RateLimitError on attempt 1
4. Orchestrator waits base_delay * backoff_multiplier^0 + jitter, then retries
5. Provider raises TimeoutError on attempt 2
6. Orchestrator waits base_delay * backoff_multiplier^1 + jitter, then retries
7. Provider succeeds on attempt 3 — orchestrator returns the LLMResponse
8. ObservabilityHooks received: on_request (attempt 1), on_error (attempt 1),
   on_request (attempt 2), on_error (attempt 2), on_request (attempt 3),
   on_response (attempt 3)
9. MetricsCollector shows: 1 total request, 1 success, 2 retries

--- Idempotency scenario ---
10. Caller calls orchestrator.execute(request) with the SAME idempotency_key
11. Orchestrator returns the cached response immediately — no provider call
12. MetricsCollector shows: 2 total requests, 2 successes (1 from cache)

--- Circuit breaker scenario ---
13. Provider fails 5 consecutive times (threshold reached)
14. Circuit breaker transitions from CLOSED → OPEN
15. Next call is rejected immediately with CircuitOpenError
16. After recovery_timeout expires, state moves to HALF_OPEN
17. Next call is allowed as a probe — if it succeeds, circuit closes
```

---

## Clarifying Questions to Ask

1. "Should retries apply to all error types or only transient ones (rate limits, timeouts)?"
2. "What is the expected max latency budget for a single orchestrated call including retries?"
3. "Should the idempotency cache have a TTL or persist indefinitely?"
4. "How many concurrent requests might the orchestrator handle — is thread safety required?"
5. "Should the circuit breaker be per-provider or global across all providers?"
6. "Do we need to support request-level timeout enforcement separate from provider timeouts?"
7. "Should observability hooks be async to avoid adding latency to the request path?"
8. "Is there a need for fallback providers when the primary circuit is open?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| LLMRequest | Immutable value object carrying prompt, model, temperature, max_tokens, and idempotency_key |
| LLMResponse | Immutable value object carrying content, model, usage stats, and latency |
| LLMProvider | Abstract interface for completing an LLMRequest and returning an LLMResponse |
| LLMOrchestrator | Core coordinator that wraps a provider with retry, caching, circuit breaking, and hooks |
| RetryPolicy | Configuration dataclass for max retries, base delay, max delay, and backoff multiplier |
| CircuitBreaker | State machine (CLOSED / HALF_OPEN / OPEN) that short-circuits calls to a failing provider |
| ObservabilityHook | Abstract callback interface for request, response, and error lifecycle events |
| MetricsCollector | Concrete hook that aggregates counts, latencies, and state transitions |
| RequestTrace | Value object capturing the full lifecycle of a single orchestrated request |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Provider abstraction, retry with backoff + jitter, idempotency cache, circuit breaker, observability hooks, metrics collector |
| v2-extended | Async provider support, persistent idempotency store, sliding-window circuit breaker, distributed tracing, fallback providers |
| v3-optimized | Connection pooling, adaptive retry policies (server-suggested delays), request prioritization, batch execution, Prometheus/OpenTelemetry export |
