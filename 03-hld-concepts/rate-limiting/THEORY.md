# Rate Limiting

## What is it?

Rate limiting is a technique used to control the number of requests a client can make to a service within a specified time window. It protects services from being overwhelmed by too many requests and ensures fair resource allocation.

## Why do we need it?

**Problem it solves**: Consider a public API receiving requests from thousands of clients:

**Without rate limiting**:
- A single client can monopolize resources
- DDoS attacks can take down the service
- No protection against accidental request floods
- Unpredictable costs for cloud resources

**With rate limiting**:
- Fair usage among all clients
- Protection against abuse and attacks
- Predictable resource consumption
- Graceful degradation under load

## Types/Approaches

### Rate Limiting Algorithms

#### 1. Token Bucket

```
         ┌─────────────────────┐
         │    Token Bucket     │
         │                     │
         │   ● ● ● ● ●        │  ← Tokens added at fixed rate
         │   ● ● ● ● ●        │
         │   ● ● ● ●          │
         │                     │
         └─────────┬───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Request arrives   │
         │   Takes 1 token     │
         └─────────────────────┘
```

**How it works**:
- Bucket holds up to N tokens (capacity)
- Tokens added at rate R per second
- Each request consumes 1 token
- Request rejected if no tokens available

**Pros**: Allows bursts up to bucket size
**Cons**: Memory for storing bucket state

#### 2. Leaky Bucket

```
    Requests
        │ │ │ │
        ▼ ▼ ▼ ▼
    ┌───────────┐
    │           │  ← Requests queue up
    │   Queue   │
    │           │
    └─────┬─────┘
          │
          ▼   Fixed rate output
    ┌───────────┐
    │  Process  │ → → → (constant rate)
    └───────────┘
```

**How it works**:
- Requests enter a queue (bucket)
- Processed at a constant rate
- Overflow rejected when queue full

**Pros**: Smooth, constant output rate
**Cons**: Doesn't handle bursts well

#### 3. Fixed Window Counter

```
    Window 1        Window 2        Window 3
    [0-60s]         [60-120s]       [120-180s]
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ Count:5 │     │ Count:2 │     │ Count:7 │
    │ Limit:5 │     │ Limit:5 │     │ Limit:5 │
    └─────────┘     └─────────┘     └─────────┘
                                         ▲
                                    2 rejected
```

**How it works**:
- Divide time into fixed windows
- Count requests per window
- Reset counter at window boundary

**Pros**: Simple, low memory
**Cons**: Boundary problem (burst at window edges)

#### 4. Sliding Window Log

```
    Requests logged with timestamps:
    [t1, t2, t3, t4, t5, t6, t7, t8]
              │                 │
              └─── Window ──────┘
                  (last 60s)
    
    Count requests in window → Compare to limit
```

**How it works**:
- Store timestamp of each request
- Count requests in sliding window
- Remove expired timestamps

**Pros**: Most accurate, no boundary issues
**Cons**: High memory for storing timestamps

#### 5. Sliding Window Counter

```
    Previous Window     Current Window
    ┌─────────────┐    ┌─────────────┐
    │  Count: 4   │    │  Count: 3   │
    └─────────────┘    └─────────────┘
          │ 25%              │ 75%
          └──────────────────┘
          Weighted: 4*0.25 + 3*0.75 = 3.25
```

**How it works**:
- Combine fixed window and sliding window
- Weight previous window by overlap %
- More accurate than fixed, less memory than log

**Pros**: Good accuracy, low memory
**Cons**: Approximation, slightly complex

### Algorithm Comparison

| Algorithm | Accuracy | Memory | Burst Handling | Complexity |
|-----------|----------|--------|----------------|------------|
| Token Bucket | Good | Low | Allows bursts | Low |
| Leaky Bucket | Good | Medium | No bursts | Medium |
| Fixed Window | Low | Very Low | Boundary bursts | Very Low |
| Sliding Window Log | Perfect | High | Accurate | Medium |
| Sliding Window Counter | Good | Low | Good | Low |

## How it works

### Basic Architecture

```
                    ┌───────────────────────────────┐
                    │           Client              │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        Rate Limiter           │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │  Check: Can proceed?    │  │
                    │  │  - Get client ID        │  │
                    │  │  - Check token/counter  │  │
                    │  │  - Allow or reject      │  │
                    │  └─────────────────────────┘  │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
              ┌─────▼─────┐                  ┌──────▼─────┐
              │  Allowed  │                  │  Rejected  │
              │   (200)   │                  │(429 / 503) │
              └───────────┘                  └────────────┘
```

### Distributed Rate Limiting

```
┌────────────┐   ┌────────────┐   ┌────────────┐
│  Server 1  │   │  Server 2  │   │  Server 3  │
└─────┬──────┘   └─────┬──────┘   └─────┬──────┘
      │                │                │
      └────────────────┼────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │     Redis      │
              │  (Central      │
              │   Counter)     │
              └────────────────┘
```

**Challenges**:
- Race conditions across servers
- Network latency to central store
- Single point of failure

**Solutions**:
- Redis with Lua scripts (atomic operations)
- Local + central hybrid
- Token bucket with periodic sync

## When to use

✅ **Use rate limiting when:**
- Protecting APIs from abuse
- Ensuring fair resource distribution
- Managing costs (pay-per-use services)
- Preventing DDoS attacks
- Controlling burst traffic

**Specific scenarios:**
- Public APIs (GitHub, Twitter API limits)
- Login endpoints (prevent brute force)
- Expensive operations (payment processing)
- Resource-intensive endpoints (file uploads)

## When NOT to use

❌ **Avoid or reconsider when:**
- Internal trusted services (may add unnecessary latency)
- Real-time critical paths (emergency services)
- Already protected by other means
- Cost of implementation exceeds benefit

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Security** | Protection from abuse | Legitimate users may be blocked |
| **Fairness** | Equal resource access | Complex to tune limits |
| **Stability** | Predictable load | Additional latency |
| **Cost** | Controlled spending | Infrastructure for rate limiting |

## Real-world examples

### GitHub API
- 5,000 requests/hour for authenticated users
- 60 requests/hour for unauthenticated
- Rate limit headers in response

### Twitter API
- Different limits per endpoint
- 15-minute windows
- Tiered by authentication level

### AWS API Gateway
- Token bucket algorithm
- Configurable requests/second
- Burst capacity separate from steady state

### Stripe
- 100 requests/second per key
- Different limits for test vs live mode
- Graceful 429 responses with retry-after

## HTTP Response Headers

```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000

{
  "error": "Rate limit exceeded",
  "message": "Try again in 60 seconds"
}
```

| Header | Description |
|--------|-------------|
| `Retry-After` | Seconds until retry allowed |
| `X-RateLimit-Limit` | Max requests in window |
| `X-RateLimit-Remaining` | Requests left in window |
| `X-RateLimit-Reset` | Unix timestamp when window resets |

## Complexity Analysis

| Algorithm | Time | Space |
|-----------|------|-------|
| Token Bucket | O(1) | O(1) per client |
| Leaky Bucket | O(1) | O(queue size) |
| Fixed Window | O(1) | O(1) per client |
| Sliding Window Log | O(n) | O(n) per client |
| Sliding Window Counter | O(1) | O(1) per client |

## Redis-Based Rate Limiting Implementation

For distributed rate limiting at scale, **Redis** is the most common implementation choice. See [Redis](../redis/) for full details on deployment and patterns.

### Why Redis for Rate Limiting?

| Feature | Benefit for Rate Limiting |
|---------|--------------------------|
| **Atomic operations** | `INCR`, `EXPIRE` guarantee no race conditions |
| **Lua scripts** | Atomic multi-command execution (check + increment) |
| **TTL support** | Automatic key expiration for time windows |
| **High throughput** | Handle millions of rate limit checks per second |
| **Distributed** | Redis Cluster for horizontal scaling |

### Redis Implementation Examples

#### Fixed Window Counter
```python
import redis
import time

r = redis.Redis()

def is_allowed_fixed_window(user_id: str, limit: int = 100, window_sec: int = 60) -> bool:
    """Fixed window counter using Redis atomic operations."""
    key = f"ratelimit:{user_id}:{int(time.time() / window_sec)}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window_sec)
    return count <= limit
```

#### Sliding Window with Sorted Sets
```python
def is_allowed_sliding_window(user_id: str, limit: int = 100, window_sec: int = 60) -> bool:
    """Sliding window using Redis sorted sets (accurate, no boundary bursts)."""
    key = f"ratelimit:{user_id}"
    now = time.time()
    window_start = now - window_sec

    # Remove old entries and count remaining
    r.zremrangebyscore(key, 0, window_start)
    count = r.zcard(key)

    if count < limit:
        r.zadd(key, {str(now): now})
        r.expire(key, window_sec)
        return True
    return False
```

#### Token Bucket with Lua Script
```python
def is_allowed_token_bucket(user_id: str, capacity: int = 100, rate: int = 10) -> bool:
    """Token bucket using atomic Lua script."""
    lua_script = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    local last_refill = tonumber(redis.call('HGET', key, 'last_refill') or now)
    local tokens = tonumber(redis.call('HGET', key, 'tokens') or capacity)

    -- Refill tokens based on elapsed time
    local elapsed = now - last_refill
    local new_tokens = math.min(capacity, tokens + elapsed * rate)

    if new_tokens >= 1 then
        redis.call('HSET', key, 'tokens', new_tokens - 1)
        redis.call('HSET', key, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)
        return 1
    else
        return 0
    end
    """
    result = r.eval(lua_script, 1, f"ratelimit:{user_id}", capacity, rate, time.time())
    return result == 1
```

**Real-world usage:**
- **Twitter API**: Redis with 15-minute sliding windows
- **Stripe**: Token bucket with Lua scripts for 100 req/sec
- **GitHub API**: Redis Cluster for distributed rate limiting

See [Redis](../redis/) for clustering, replication, and production deployment patterns.

## Key Takeaways

1. **Choose the right algorithm**: Token bucket for APIs with burst tolerance; sliding window for accuracy

2. **429 vs 503**: Return 429 (Too Many Requests) for rate limiting, 503 for server overload

3. **Include headers**: Always tell clients their limits and when to retry

4. **Distributed is hard**: Use Redis with Lua scripts for atomic operations across servers

5. **Multi-tier limits**: Different limits per user tier, per endpoint, per time window

---

## GenAI Notes

Rate limiting takes on additional importance in LLM-powered systems due to the high cost and latency of model inference:

| GenAI Rate-Limiting Pattern | Description | Why It Matters |
|----------------------------|-------------|----------------|
| **Token-based rate limiting** | Limit by tokens-per-minute (TPM) rather than requests-per-second | A single LLM request can consume thousands of tokens; request count alone is misleading |
| **Model provider throttling** | Respect upstream rate limits from providers (OpenAI, Anthropic, etc.) | Avoid 429 errors and account suspension; implement client-side token bucket |
| **Cost caps** | Set per-user or per-tenant spending limits (daily/monthly) | Prevent runaway costs from long prompts or agent loops |
| **Prompt-size gating** | Reject or truncate prompts exceeding a token threshold before they reach the model | Protect against adversarial mega-prompts that inflate cost and latency |

**Key differences from classical rate limiting:**
- **Unit of measure shifts**: From requests/sec to tokens/min. A single "request" may cost 100× more than another depending on prompt length.
- **Cascading limits**: You rate-limit your own API, but also must respect third-party provider limits downstream.
- **Abuse vectors expand**: Adversaries can craft prompts designed to maximize token consumption or trigger expensive tool-use loops.

> **Deep dive →** [Safety & Governance](../../06-genai-systems/00-concepts/safety-governance/) · [LLM-Oriented System Design](../../06-genai-systems/00-concepts/llm-system-design/)

---

## Related Concepts
- [API Gateway](../api-gateway/) - Often implements rate limiting at gateway level
- [Load Balancing](../load-balancing/) - Distributes load, rate limiting controls it
- [CDN](../cdn/) - Can apply rate limiting at edge
- [Redis](../redis/) - Primary implementation for distributed rate limiting with atomic operations

---

## Distributed Policy Hierarchy

In production, one limit is rarely enough. A practical limiter evaluates a hierarchy of policies in order:

1. Global safety policy (`all traffic <= X req/s`)
2. Tenant or API-key policy (`tenant <= Y req/min`)
3. Identity policy (`user_id` or `ip` limits)
4. Endpoint policy (`/search` tighter than `/profile`)
5. Optional method/action policy (write endpoints stricter than read endpoints)

The request is allowed only if it passes all applicable policies. This layered model prevents bypass where a single dimension (for example IP) is rotated.

### Evaluation Strategy

- Compute all candidate keys for the request.
- Check the strictest policies first to short-circuit quickly.
- Return the most restrictive violation in the response metadata.

---

## Hot-Key Handling

Hot keys occur when one identity or endpoint receives disproportionate traffic. A single key can saturate one Redis shard even when cluster-wide utilization is healthy.

Common mitigations:

- Key bucketing for safe workloads (`user:123:bucket:0..n`) with deterministic merge logic
- Local short-lived shield cache for immediate repeat denies
- Per-key circuit breaker when downstream limiter storage is overloaded
- Isolate known heavy policies into dedicated shards or clusters
- Pre-aggregation windows for very high-frequency counters

Important trade-off: stronger mitigation improves stability but may add approximation error. Keep this explicit in interview discussions.

---

## Fail-Open vs Fail-Closed

When limiter storage is unavailable (for example Redis outage), services must choose behavior:

| Mode | Behavior | Strength | Risk |
|---|---|---|---|
| Fail-open | Allow requests when limiter check cannot complete | Availability | Potential overload and abuse |
| Fail-closed | Reject requests when limiter check cannot complete | Protection | User-visible downtime |
| Hybrid | Per-endpoint decision (critical writes closed, reads open) | Balanced | More operational complexity |

A common policy is hybrid:

- Authentication, payment, expensive writes: fail-closed
- Read-heavy browse endpoints: fail-open with emergency caps

---

## Low-Latency Check Budget

Limiter checks are in the critical path, so budget them explicitly:

- p50: <= 2 ms
- p95: <= 5 ms
- p99: <= 10 ms

Techniques to stay within budget:

- Persistent connections and command pipelining to Redis
- Single round-trip atomic Lua operations
- Local in-process pre-check for obvious denies
- Timeout budget with deterministic fallback mode

---

## HTTP 429 Contract

A strong rate-limiting API returns consistent `429` responses:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

And a compact JSON body:

```json
{
  "error": "rate_limit_exceeded",
  "policy": "user_per_minute",
  "retry_after_seconds": 12
}
```

This gives clients enough information to implement proper backoff and avoid retry storms.

---

## HLD to LLD Bridge

Interviewers often move from architecture to code-level design. Map concepts directly:

- HLD policy hierarchy -> LLD `RateLimitConfig` + policy evaluation chain
- HLD distributed atomicity -> LLD `DistributedQuotaStore` interface
- HLD fail-mode decision -> LLD `FailureModeStrategy`
- HLD headers and metadata -> LLD `RateLimitResult#getHeaders`

See the paired LLD project:
- [Rate Limiter Problem](../../02-lld-projects/rate-limiter/PROBLEM.md)
- [Rate Limiter Design](../../02-lld-projects/rate-limiter/DESIGN.md)

## 📊 Diagrams

- [Token bucket vs sliding window decision flow](./diagrams/token-bucket-vs-sliding-window.mmd) - how each algorithm decides a request: token bucket consumes one token if available and refills at a fixed rate, while sliding window counter weights the previous window by overlap and adds the current count before comparing against the limit.
