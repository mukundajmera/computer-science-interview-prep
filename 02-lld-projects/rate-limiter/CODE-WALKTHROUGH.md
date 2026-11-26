# Code Walkthrough: Rate Limiter

## Overview

Essential for API design interviews. Controls request throughput.

---

## File Structure

```
java/v1-basic/
├── RateLimiter.java       # Abstract + Token Bucket
├── SlidingWindowLog.java  # Sliding window implementation
├── LeakyBucket.java       # Leaky bucket variant
└── RateLimiterDemo.java   # Demo entry point
```

---

## Algorithms Comparison

| Algorithm | Pros | Cons | Use Case |
|-----------|------|------|----------|
| **Token Bucket** | Allows bursts | Complex | API rate limiting |
| **Leaky Bucket** | Smooth output | No bursts | Traffic shaping |
| **Fixed Window** | Simple | Edge bursts | Basic limiting |
| **Sliding Window** | Accurate | Memory cost | Precise limiting |

---

## Token Bucket Algorithm

```
Initialization:
- bucket = maxTokens
- lastRefillTime = now

allow(request):
1. Refill tokens based on elapsed time
2. If tokens >= 1:
   - Consume 1 token
   - Return true (allowed)
3. Else:
   - Return false (rejected)
```

### Key Formula
```
tokensToAdd = elapsedTime × refillRate
bucket = min(bucket + tokensToAdd, maxTokens)
```

---

## Design Pattern: Strategy

```java
interface RateLimiter {
    boolean allow(String clientId);
}

class TokenBucket implements RateLimiter { ... }
class SlidingWindow implements RateLimiter { ... }
class LeakyBucket implements RateLimiter { ... }
```

---

## Interview Questions

### 1. "How to make distributed?"

Options:
- Redis + Lua scripts (atomic operations)
- Consistent hashing for partitioning
- Centralized rate limit service

### 2. "How to handle different limits per user?"

```java
Map<String, RateLimiter> userLimiters;
// Or: Map<UserTier, RateLimiter> tierLimiters;
```

### 3. "Token Bucket vs Leaky Bucket?"

- **Token Bucket**: Allows bursts up to bucket size
- **Leaky Bucket**: Constant output rate, no bursts

### 4. "How does Redis implement this?"

Redis `INCR` with `EXPIRE` for fixed window, or sorted sets for sliding window.

---

## Complexity

| Algorithm | Time | Space |
|-----------|------|-------|
| Token Bucket | O(1) | O(1) per client |
| Fixed Window | O(1) | O(1) per client |
| Sliding Window Log | O(n) cleanup | O(n) timestamps |
| Sliding Window Counter | O(1) | O(1) per client |

Where n = requests in window
