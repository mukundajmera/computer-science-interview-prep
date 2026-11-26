# Interview Questions: Rate Limiting

## Basic Questions

### 1. What is rate limiting and why do we need it?
**Q**: Explain what rate limiting is and its purpose in distributed systems.

**A**: Rate limiting controls the number of requests a client can make within a time period.

**Purposes:**
- **Prevent abuse**: Stop malicious users from overwhelming the system
- **Ensure fairness**: Equal access for all users
- **Protect resources**: Prevent cascading failures from overload
- **Control costs**: Limit expensive operations
- **Maintain SLAs**: Ensure predictable performance

**Example**: Twitter API limits to 300 tweets/3 hours to prevent spam.

---

### 2. What are the main rate limiting algorithms?
**Q**: Describe common rate limiting algorithms and their trade-offs.

**A**:

| Algorithm | How it Works | Pros | Cons |
|-----------|--------------|------|------|
| **Token Bucket** | Tokens refill at steady rate, requests consume tokens | Allows bursts, smooth rate | Memory for bucket state |
| **Leaky Bucket** | Queue processes at constant rate | Smooth output, simple | No burst handling |
| **Fixed Window** | Counter per time window | Very simple, low memory | Boundary burst problem |
| **Sliding Window Log** | Store timestamps, count in window | Most accurate | High memory |
| **Sliding Window Counter** | Weighted average of windows | Good accuracy, low memory | Approximation |

---

### 3. What is the boundary problem in fixed window rate limiting?
**Q**: Explain the boundary problem and how to solve it.

**A**: The boundary problem allows 2x the intended rate at window boundaries.

**Problem:**
```
Window 1 (0-60s)    Window 2 (60-120s)
        │                 │
    [─────────]       [─────────]
         ↓ 100 req        ↓ 100 req
       at 59s           at 61s
       
Result: 200 requests in 2 seconds!
```

**Solutions:**
1. **Sliding Window Log**: Track exact timestamps
2. **Sliding Window Counter**: Weighted average
3. **Shorter windows**: Reduce impact but increase overhead

---

### 4. How does the token bucket algorithm work?
**Q**: Explain token bucket in detail with an example.

**A**: Token bucket allows controlled bursting while maintaining average rate.

**Components:**
- **Bucket capacity**: Maximum tokens (burst size)
- **Refill rate**: Tokens added per second
- **Token count**: Current tokens in bucket

**Example: 10 tokens/second, capacity 50**
```
Initial:    50 tokens (full)
Request 1:  49 tokens (allowed)
...
Request 50: 0 tokens (allowed)
Request 51: 0 tokens (REJECTED)

After 1 second: 10 tokens refilled
Request 52: 9 tokens (allowed)
```

**Code logic:**
```python
def allow_request():
    refill_tokens()  # Add tokens based on time elapsed
    if tokens >= 1:
        tokens -= 1
        return True
    return False
```

---

### 5. What HTTP status code should you return when rate limited?
**Q**: What response should a rate-limited request receive?

**A**: Return **429 Too Many Requests** with helpful headers.

**Response:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
Content-Type: application/json

{
    "error": "rate_limit_exceeded",
    "message": "Rate limit of 100 requests per minute exceeded",
    "retry_after_seconds": 30
}
```

**Headers explained:**
- `Retry-After`: When client can retry
- `X-RateLimit-Limit`: Max requests allowed
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

---

## Intermediate Questions

### 1. How do you implement distributed rate limiting?
**Q**: Rate limiting across multiple servers is challenging. How would you implement it?

**A**: Use a centralized store with atomic operations.

**Architecture:**
```
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Server A │   │ Server B │   │ Server C │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
              ┌─────▼─────┐
              │   Redis   │
              │           │
              │  User123  │──► tokens: 5
              │  User456  │──► tokens: 0
              └───────────┘
```

**Redis + Lua Script (atomic):**
```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, window)
end

if current > limit then
    return 0  -- Rejected
end
return 1  -- Allowed
```

**Challenges:**
- Network latency to Redis
- Redis as single point of failure
- Consistency during Redis failover

---

### 2. How do you handle rate limiting for different user tiers?
**Q**: Free users get 100 req/min, premium users get 1000 req/min. How do you implement this?

**A**: Implement tiered rate limiting with configurable limits.

```python
TIER_LIMITS = {
    "free": {"requests": 100, "window": 60},
    "basic": {"requests": 500, "window": 60},
    "premium": {"requests": 1000, "window": 60},
    "enterprise": {"requests": 10000, "window": 60},
}

def check_rate_limit(user_id, tier):
    limits = TIER_LIMITS[tier]
    key = f"rate:{user_id}"
    
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, limits["window"])
    
    if count > limits["requests"]:
        return False, limits
    
    return True, limits
```

**Additional considerations:**
- Separate limits per endpoint (login stricter than read)
- Burst allowances for premium tiers
- Graceful degradation (soft vs hard limits)

---

### 3. What's the difference between rate limiting and throttling?
**Q**: Explain the difference between rate limiting and throttling.

**A**:

| Aspect | Rate Limiting | Throttling |
|--------|---------------|------------|
| **Action** | Reject excess requests | Slow down requests |
| **Response** | 429 error | Delayed processing |
| **Client experience** | Immediate rejection | Slower response |
| **Use case** | API protection | Resource protection |

**Throttling example:**
```python
def throttled_request(request):
    # Instead of rejecting, delay processing
    delay = calculate_delay(request.user)
    time.sleep(delay)
    return process_request(request)
```

**When to use each:**
- Rate limiting: When you want clients to know they're over limit
- Throttling: When you want to gracefully degrade without errors

---

### 4. How do you implement rate limiting at different layers?
**Q**: Where can rate limiting be implemented in a system?

**A**: Rate limiting can be applied at multiple layers:

```
┌─────────────────────────────────────────────────────────────┐
│                         CDN Edge                             │
│            (Cloudflare, Akamai - DDoS protection)           │
├─────────────────────────────────────────────────────────────┤
│                        Load Balancer                         │
│              (Nginx, HAProxy - connection limits)            │
├─────────────────────────────────────────────────────────────┤
│                        API Gateway                           │
│          (Kong, AWS API Gateway - API rate limits)           │
├─────────────────────────────────────────────────────────────┤
│                       Application                            │
│            (Business logic, user-specific limits)            │
├─────────────────────────────────────────────────────────────┤
│                         Database                             │
│                   (Connection pooling)                       │
└─────────────────────────────────────────────────────────────┘
```

**Each layer handles different concerns:**
- **CDN**: Block attacks before they reach origin
- **Load Balancer**: Protect backend servers
- **API Gateway**: Apply per-API/per-user limits
- **Application**: Business-specific rules

---

### 5. How do you handle rate limit synchronization across data centers?
**Q**: You have servers in US, EU, and Asia. How do you coordinate rate limits?

**A**: Several strategies depending on consistency requirements:

**1. Local + Global (Hybrid)**
```
┌─────────────────────────────────────────────────────────────┐
│                     User: 1000 req/min global                │
│                                                              │
│   US Region          EU Region          Asia Region          │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐          │
│  │Local: 50│        │Local: 50│        │Local: 50│          │
│  └────┬────┘        └────┬────┘        └────┬────┘          │
│       │                  │                  │                │
│       └──────────────────┼──────────────────┘                │
│                          │                                   │
│                    ┌─────▼─────┐                             │
│                    │Global Sync│ (periodic, async)           │
│                    └───────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

**2. Per-region limits**
- Each region has independent limits
- Simpler but user can get 3x by hitting all regions

**3. Sticky routing**
- Route user to same region consistently
- Use consistent hashing on user ID

---

## Advanced Questions

### 1. Design a rate limiter for 1 billion requests per day
**Q**: How would you design a rate limiter handling massive scale?

**A**: **Requirements:**
- 1B requests/day ≈ 12,000 requests/second
- 100M unique users
- Multiple data centers

**Design:**

```
                    ┌─────────────────────────────────┐
                    │        Edge Rate Limiter        │
                    │     (Cloudflare, per-IP)        │
                    └───────────────┬─────────────────┘
                                    │
                    ┌───────────────▼─────────────────┐
                    │       API Gateway Cluster       │
                    │    (Kong/Nginx, per-API key)    │
                    └───────────────┬─────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
    ┌─────▼─────┐             ┌─────▼─────┐             ┌─────▼─────┐
    │  App Pod  │             │  App Pod  │             │  App Pod  │
    │┌─────────┐│             │┌─────────┐│             │┌─────────┐│
    ││Local    ││             ││Local    ││             ││Local    ││
    ││Cache    ││             ││Cache    ││             ││Cache    ││
    │└────┬────┘│             │└────┬────┘│             │└────┬────┘│
    └─────┼─────┘             └─────┼─────┘             └─────┼─────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   Redis Cluster   │
                          │ (Sharded by user) │
                          └───────────────────┘
```

**Key decisions:**
1. **Multi-layer**: Edge blocks attacks, app handles business logic
2. **Local caching**: Reduce Redis calls, sync periodically
3. **Sharding**: Partition by user ID across Redis nodes
4. **Approximate**: Allow small over-limit for performance

---

### 2. How do you prevent rate limit bypass using distributed IPs?
**Q**: An attacker uses many IP addresses to bypass per-IP rate limits. How do you handle this?

**A**: **Defense in depth approach:**

**1. Multi-dimensional limiting**
```python
limits = {
    "per_ip": {"limit": 100, "window": 60},
    "per_user": {"limit": 1000, "window": 60},
    "per_api_key": {"limit": 5000, "window": 60},
    "global": {"limit": 100000, "window": 60},
}

def check_all_limits(request):
    if not check_limit("ip", request.ip):
        return False
    if not check_limit("user", request.user_id):
        return False
    if not check_limit("api_key", request.api_key):
        return False
    if not check_limit("global", "all"):
        return False
    return True
```

**2. Behavioral analysis**
- Track patterns, not just counts
- ML models to detect anomalies
- Device fingerprinting

**3. Challenge mechanisms**
- CAPTCHA after threshold
- Proof of work
- Bot detection (reCAPTCHA)

---

### 3. How do you implement graceful degradation with rate limiting?
**Q**: Instead of hard rejecting, how can you gracefully degrade service?

**A**: **Soft limits with progressive degradation:**

```python
class GracefulRateLimiter:
    def check_request(self, user_id, request_type):
        usage_percent = self.get_usage_percent(user_id)
        
        if usage_percent < 80:
            return Response.FULL_SERVICE
        elif usage_percent < 100:
            return Response.DEGRADED  # Reduced features
        elif usage_percent < 120:
            return Response.MINIMAL   # Cached/stale data
        else:
            return Response.REJECTED  # Hard limit
    
    def handle_degraded(self, request):
        # Disable expensive features
        response = process_request(request)
        response.disable_recommendations()
        response.disable_analytics()
        return response
```

**Degradation strategies:**
1. **Feature reduction**: Disable non-critical features
2. **Lower quality**: Reduce image resolution, sample data
3. **Cached responses**: Serve stale but fast data
4. **Queue for later**: Accept but process async

---

## Common Follow-ups

- "How would you test that rate limiting works correctly?"
- "What happens during a Redis failover?"
- "How do you set the right rate limits?"
- "How do you communicate limits to users?"
- "How do you handle rate limiting for WebSocket connections?"

---

## Red Flags to Avoid

❌ **Don't say:**
- "Just use fixed window, it's simple" — Shows ignorance of boundary problem
- "Store every request timestamp" — Doesn't scale
- "Rate limit at application only" — Ignores edge protection
- "Same limits for all users" — Poor user experience

❌ **Don't forget:**
- Response headers for client guidance
- Different limits for different endpoints
- Handling clock skew in distributed systems
- Graceful degradation vs hard rejection

---

## How to Explain in 30 Seconds

> "Rate limiting controls how many requests a client can make in a time window. The key algorithms are token bucket (allows bursts, used by AWS) and sliding window (accurate, used for strict limits). For distributed systems, use Redis with Lua scripts for atomic operations. Always return 429 status with Retry-After header. Apply limits at multiple layers: edge for DDoS protection, API gateway for per-user limits, and application for business rules."

---

## Deep-Dive Questions (Distributed Production)

### 1. How do you evaluate multiple rate-limit policies in one request?
**Q**: A request should satisfy global, tenant, user, and endpoint limits. How do you evaluate this efficiently?

**A**:

1. Build a deterministic ordered policy list (strictest first).
2. Generate keys for all applicable policies.
3. Use one atomic script call per policy or one batched script for all keys.
4. Short-circuit on the first failing policy and return that policy in the response.

Pseudo-flow:

```text
resolve policies -> build keys -> atomic checks -> first failure? -> 429 with policy_id
```

This keeps behavior predictable and prevents bypass via dimension switching.

---

### 2. How do you handle hot keys?
**Q**: One endpoint key is far hotter than the rest and a single shard is overloaded. What do you do?

**A**:

- Confirm skew with top-key metrics first.
- Apply short-term shielding:
  - local deny cache for repeatedly failing keys
  - temporary per-key stricter ceiling
  - backpressure on high-cost endpoints
- Apply structural fixes:
  - key bucketing for valid workloads
  - dedicated shard/cluster for heavy policy namespaces
  - isolate expensive write-path policies from normal read policies

Key point: hot-key mitigation is usually layered, not a single fix.

---

### 3. Fail-open vs fail-closed: how do you choose?
**Q**: Redis is unavailable for rate-limit checks. Should requests pass or be blocked?

**A**:

Use per-endpoint failure policy:

- Fail-closed for security and expensive mutation endpoints
- Fail-open for read-heavy low-risk endpoints
- Require explicit defaults and alerting for both paths

You should also cap fail-open with emergency static thresholds to avoid total overload.

---

### 4. How do you keep check latency under 10 ms?
**Q**: What concrete design choices keep limiter overhead low?

**A**:

- Single round-trip Lua scripts instead of multi-command read/modify/write
- Persistent pooled connections
- Pipelining when evaluating multiple policies
- Small payload keys and compact serialized state
- Timeouts with deterministic fallback mode

You should track p50/p95/p99 latency separately for limiter checks, not only end-to-end API latency.

---

### 5. What should a complete 429 response include?
**Q**: Beyond HTTP status code, what should the response contract look like?

**A**:

Headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

Body:

```json
{
  "error": "rate_limit_exceeded",
  "policy": "user_per_minute",
  "retry_after_seconds": 12
}
```

This allows clients to implement adaptive retry and avoids blind hammering.

---

### 6. How do you bridge HLD discussion to LLD implementation?
**Q**: Interviewer asks, "Show me how this architecture maps to code."

**A**:

Map each architecture component to a code abstraction:

- Policy hierarchy -> `RateLimitPolicy` and policy evaluator chain
- Counter store -> `DistributedQuotaStore` interface
- Failure handling -> `FailureModeStrategy` (`FAIL_OPEN`, `FAIL_CLOSED`, hybrid)
- HTTP response contract -> `RateLimitResult` with header helper

Then explain which parts are in-memory for single-node and which move to Redis for distributed mode.
