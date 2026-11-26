# Design Approach for LLM Request Orchestrator

A step-by-step thought process for designing the LLM request orchestrator.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| LLM Request | ✅ Yes | Input value object carrying prompt and parameters |
| LLM Response | ✅ Yes | Output value object with content and metadata |
| LLM Provider | ✅ Yes | Abstract backend that processes requests |
| Orchestrator | ✅ Yes | Central coordinator adding resilience layers |
| Retry Policy | ✅ Yes | Configuration controlling retry behavior |
| Circuit Breaker | ✅ Yes | State machine protecting against cascading failures |
| Observability Hook | ✅ Yes | Callback interface for lifecycle events |
| Metrics Collector | ✅ Yes | Concrete hook aggregating operational metrics |
| Request Trace | ✅ Yes | Record of a single request's full lifecycle |
| Idempotency Cache | ❌ No | Internal data structure (dict), not a separate entity |
| Jitter | ❌ No | Algorithm detail inside retry logic |

**Final Entities**: LLMRequest, LLMResponse, LLMProvider, LLMOrchestrator, RetryPolicy, CircuitBreaker, ObservabilityHook, MetricsCollector, RequestTrace

---

## Step 2: Define Relationships

```
LLMOrchestrator (1) ──wraps──> (1) LLMProvider
LLMOrchestrator (1) ──uses──> (1) RetryPolicy
LLMOrchestrator (1) ──uses──> (1) CircuitBreaker
LLMOrchestrator (1) ──notifies──> (n) ObservabilityHook
LLMOrchestrator (1) ──caches──> (n) LLMResponse  [keyed by idempotency_key]
LLMProvider (1) ──accepts──> (n) LLMRequest
LLMProvider (1) ──returns──> (n) LLMResponse
MetricsCollector ──implements──> ObservabilityHook
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| Orchestrator → Provider | Composition | Provider is injected and owned by orchestrator |
| Orchestrator → RetryPolicy | Aggregation | Policy is a config object, can be shared |
| Orchestrator → CircuitBreaker | Composition | Each orchestrator manages its own breaker |
| Orchestrator → ObservabilityHook | Aggregation | Hooks are externally provided |
| MetricsCollector → ObservabilityHook | Inheritance | MetricsCollector is a concrete hook |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Proxy / Decorator** | ✅ Yes | Orchestrator wraps provider calls with cross-cutting concerns |
| **Strategy** | ✅ Yes | RetryPolicy is a swappable strategy for retry behavior |
| **Observer** | ✅ Yes | Observability hooks are notified at each lifecycle stage |
| **Circuit Breaker** | ✅ Yes | Dedicated state machine protecting against cascading failure |
| **Template Method** | 🔄 v2 | Common retry loop with customizable steps |
| **Chain of Responsibility** | ❌ No | Single orchestrator is sufficient; no chain needed |

### Pattern Application:

1. **Proxy / Decorator Pattern** — LLMOrchestrator
   - Wraps any `LLMProvider` implementation transparently
   - Adds retry, caching, circuit breaking without modifying the provider
   - Caller interacts with the orchestrator using the same `execute()` signature

2. **Strategy Pattern** — RetryPolicy
   - Encapsulates retry parameters (max retries, delays, multiplier)
   - Different policies can be swapped per use case (aggressive, conservative, no-retry)
   - Decouples retry configuration from retry execution

3. **Observer Pattern** — ObservabilityHook
   - Multiple hooks can be registered (logging, metrics, tracing)
   - Hooks are notified on request, response, and error events
   - Adding a new hook requires zero changes to orchestrator code

4. **Circuit Breaker Pattern** — CircuitBreaker
   - Three states: CLOSED (allow), OPEN (reject), HALF_OPEN (probe)
   - Transitions based on consecutive failures and recovery timeout
   - Prevents wasting resources on a known-failing provider

---

## Step 4: Design Classes

### Core Classes:

#### LLMRequest (Dataclass)
- **Attributes**:
  - `prompt: str` — The input text
  - `model: str` — Target model identifier
  - `temperature: float` — Sampling temperature
  - `max_tokens: int` — Maximum tokens in response
  - `idempotency_key: Optional[str]` — Cache key for deduplication
- **Design Note**: Immutable value object; no methods beyond field access

#### LLMResponse (Dataclass)
- **Attributes**:
  - `content: str` — Generated text
  - `model: str` — Model that produced the response
  - `usage: dict` — Token usage breakdown (prompt_tokens, completion_tokens, total_tokens)
  - `latency_ms: float` — Provider call duration in milliseconds
- **Design Note**: Immutable value object returned by provider and cached

#### LLMProvider (ABC)
- **Methods**:
  - `complete(request: LLMRequest) -> LLMResponse` — Send request, return response
- **Implementations**: MockProvider (testing), OpenAIProvider (v2), AnthropicProvider (v2)

#### LLMOrchestrator
- **Attributes**:
  - `provider: LLMProvider` — Wrapped backend
  - `retry_policy: RetryPolicy` — Retry configuration
  - `circuit_breaker: CircuitBreaker` — Failure state machine
  - `hooks: List[ObservabilityHook]` — Registered lifecycle observers
  - `_idempotency_cache: Dict[str, LLMResponse]` — Cached responses
- **Methods**:
  - `execute(request: LLMRequest) -> LLMResponse` — Main entry point
  - `add_hook(hook: ObservabilityHook) -> None` — Register an observer
- **Internal Flow**:
  1. Check idempotency cache → return if hit
  2. Check circuit breaker → raise if open
  3. Call provider with retry loop
  4. On success: cache response, record success, notify hooks
  5. On failure: record failure, notify hooks, maybe open circuit

#### RetryPolicy (Dataclass)
- **Attributes**:
  - `max_retries: int` — Maximum retry attempts (default 3)
  - `base_delay: float` — Initial delay in seconds (default 1.0)
  - `max_delay: float` — Delay cap in seconds (default 30.0)
  - `backoff_multiplier: float` — Exponential multiplier (default 2.0)

#### CircuitBreaker
- **Attributes**:
  - `failure_threshold: int` — Failures before opening (default 5)
  - `recovery_timeout: float` — Seconds before half-open (default 30.0)
  - `state: CircuitState` — Current state (CLOSED / OPEN / HALF_OPEN)
  - `failure_count: int` — Consecutive failure counter
  - `last_failure_time: float` — Timestamp of last failure
- **Methods**:
  - `allow_request() -> bool` — Check if a call is permitted
  - `record_success() -> None` — Reset failure count, close circuit
  - `record_failure() -> None` — Increment count, possibly open circuit

#### ObservabilityHook (ABC)
- **Methods**:
  - `on_request(request, attempt)` — Called before each provider call
  - `on_response(request, response, attempt)` — Called on success
  - `on_error(request, error, attempt)` — Called on each failure

#### MetricsCollector (ObservabilityHook)
- **Attributes**:
  - `total_requests: int`
  - `successes: int`
  - `failures: int`
  - `retries: int`
  - `latencies: List[float]`
  - `circuit_state_changes: List[tuple]`
- **Methods**:
  - `get_latency_percentile(p: float) -> float` — Compute p-th percentile
  - `get_error_rate() -> float` — failures / total_requests

---

## Step 5: Handle Edge Cases

### Input Validation:
- None or empty prompt in LLMRequest
- Negative max_retries or base_delay in RetryPolicy
- Invalid temperature (outside 0.0–2.0)

### Retry Logic:
- Non-retryable errors (e.g., authentication failure) must not be retried
- All retries exhausted — raise the last error
- Backoff delay exceeds max_delay — cap at max_delay

### Circuit Breaker:
- Circuit opens mid-retry — remaining attempts should be skipped
- Half-open probe fails — circuit returns to OPEN
- Half-open probe succeeds — circuit closes, failure count resets
- Clock skew in recovery timeout (use monotonic time)

### Idempotency:
- Cache collision with different prompts but same key — trust the key, return cached value
- Cache grows unbounded — acceptable in v1; add TTL in v2

### Observability:
- Hook raises an exception — catch and suppress; never disrupt the request path
- Hook blocks for a long time — acceptable in v1 (synchronous hooks); async hooks in v2

---

## Step 6: Optimization Opportunities

### Data Structures:

| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Idempotency lookup | O(n) list scan | O(1) dict lookup |
| Latency percentile | O(n log n) sort | O(n log n) with sorted insert (v2) |
| Circuit state check | O(1) | O(1) — already optimal |

### Backoff Calculation:
- Use `min(base_delay * multiplier^attempt, max_delay) + jitter` to prevent unbounded waits
- Jitter: `random.uniform(0, 1) * base_delay` decorrelates retries across clients

### Memory:
- Idempotency cache bounded by key count — add LRU eviction in v2
- Metrics latencies list grows unbounded — add reservoir sampling in v3

---

## Step 7: Version Progression

### v1-basic
- Synchronous provider wrapper
- Retry with exponential backoff + jitter
- In-memory idempotency cache (dict)
- Simple circuit breaker (consecutive failures)
- Observer-pattern hooks (logging, metrics)
- Full test suite with MockProvider

### v2-extended
- Async provider support (`asyncio`)
- Persistent idempotency store (SQLite / Redis adapter)
- Sliding-window circuit breaker
- Distributed tracing (OpenTelemetry-compatible spans)
- Fallback provider chain
- Request timeout enforcement

### v3-optimized
- Connection pooling and keep-alive
- Adaptive retry (honor Retry-After headers)
- Request prioritization and queuing
- Batch execution for multiple requests
- Prometheus / OpenTelemetry metrics export
- LRU cache with TTL for idempotency

---

## Code Organization

```
llm-request-orchestrator/
├── PROBLEM.md                     # Problem statement
├── APPROACH.md                    # This design walkthrough
├── DESIGN.md                      # Class diagrams and decisions
└── python/
    ├── v1-basic/
    │   ├── __init__.py            # Package marker
    │   ├── provider.py            # LLMProvider ABC, MockProvider, error hierarchy
    │   ├── orchestrator.py        # LLMOrchestrator, RetryPolicy, CircuitBreaker
    │   ├── observability.py       # ObservabilityHook, LoggingHook, MetricsCollector
    │   └── demo.py                # Runnable demonstration
    └── tests/
        ├── __init__.py            # Package marker
        └── test_orchestrator.py   # Full test suite (15+ test methods)
```

---

## Interview Discussion Points

1. **Why Proxy/Decorator over Middleware Chain?**
   - Single orchestrator keeps the call path simple and debuggable
   - Middleware chains add indirection; premature for a focused wrapper
   - Trade-off: less composable — but clarity wins in an interview

2. **Why Observer for Observability?**
   - Decouples metrics/logging from orchestration logic
   - Adding a new hook is zero-change to existing code
   - Alternative: aspect-oriented programming (overkill for Python)

3. **Why a separate CircuitBreaker class?**
   - Single Responsibility: breaker logic is independently testable
   - Reusable across multiple orchestrators or providers
   - State machine pattern maps cleanly to CLOSED / OPEN / HALF_OPEN

4. **Idempotency trade-offs?**
   - In-memory cache is fast but not durable (lost on restart)
   - Key collisions trusted by design — caller is responsible for key uniqueness
   - v2 adds persistent store for cross-process deduplication
