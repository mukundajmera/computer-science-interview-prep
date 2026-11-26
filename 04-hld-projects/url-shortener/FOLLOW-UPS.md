# URL Shortener — Follow-Up Questions

## 1. How do you guarantee uniqueness for short codes?

Use monotonic ID range allocation (or region-partitioned ranges), then base62 encode. Keep random fallback only for vanity/custom flows.

## 2. What if redirects spike 20x for a viral link?

Apply cache replication for hot keys, local process cache, and circuit breakers to protect the primary store.

## 3. Should same long URL always map to same short URL?

Add optional deterministic mode using canonicalized URL hash + conditional write. Keep default non-deterministic for product flexibility.

## 4. How would you support multi-region active writes?

Partition key ranges by region and replicate mapping tables asynchronously. Resolve alias conflicts via regional ownership rules.

## 5. How do you add richer analytics without harming redirect latency?

Emit click events asynchronously, aggregate in streaming jobs, and expose read APIs over analytics store only.

## 6. How do you reduce abuse/phishing risk?

Rate-limit create APIs, integrate URL reputation checks, quarantine suspicious links, and provide report workflows.

## 7. How do you support short-link expiration and legal takedown?

Use status fields (`ACTIVE`, `EXPIRED`, `DISABLED`) and enforce redirect decision logic before cache response.

---

## Pattern Integration Addendum

### 7. "How would you choose transport/channel strategy under changing realtime requirements?"

#### Why They Ask

Tests whether you can avoid defaulting to a single transport and instead choose based on interaction model, freshness target, and connection cost.

#### Approach

- **Channel matrix:** Polling for low-frequency updates, long polling for compatibility fallback, SSE for one-way server push, WebSocket for bidirectional high-frequency flows.
- **Fallback policy:** Keep a deterministic downgrade path (`websocket -> sse -> long polling`) for restrictive networks.
- **Ordering + replay:** Assign monotonic event IDs and replay missed ranges after reconnect.
- **Connection management:** Maintain user-to-connection mapping with heartbeat and idle timeouts.

#### Key trade-off

A richer realtime channel improves UX but increases stateful infrastructure complexity and connection operating cost.

### 8. "How would you escalate contention strategy as load and conflict rates increase?"

#### Why They Ask

Probes whether you can pick the least-complex coordination model first, then escalate only when measured conflict pressure justifies it.

#### Approach

- **Start optimistic:** Version-check + bounded retry for low conflict workloads.
- **Escalate selectively:** Move hot keys to pessimistic lock or serialized queue lanes.
- **Distributed coordination:** Use distributed lock only when cross-node exclusivity is truly required.
- **Safety controls:** Add idempotency keys, retry jitter, lock timeout, and deadlock avoidance rules.

#### Key trade-off

Stronger coordination raises correctness confidence but can reduce throughput and availability under peak contention.

### 9. "How would you make multi-step flows durable and retry-safe?"

#### Why They Ask

Tests your ability to keep business consistency across partial failures in workflows that span services and time.

#### Approach

- **State machine first:** Define explicit lifecycle states and transition guards.
- **Saga style:** Commit each step independently with compensating actions for rollback.
- **Durability:** Persist workflow checkpoints before advancing to the next step.
- **Idempotency:** Require stable idempotency keys for all side-effecting steps.
- **Versioning:** Keep old workflow definitions alive for in-flight instances during upgrades.

#### Key trade-off

Durable orchestration improves resilience and observability but adds runtime overhead and operational complexity.

