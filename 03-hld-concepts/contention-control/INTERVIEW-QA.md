# Interview Questions: Contention Control

## Basic Questions

### 1. What is the first step when you detect contention?
**A**: Identify the exact resource key and invariant being violated, then pick the lowest-complexity coordination policy that preserves correctness.

### 2. When should you use optimistic concurrency?
**A**: When conflicts are rare and retry cost is acceptable.

### 3. When should you use pessimistic locking?
**A**: When conflict probability is high and retries become too expensive or unsafe.

## Intermediate Questions

### 4. How do you avoid retry storms with OCC?
**A**: Add bounded retries, exponential backoff with jitter, and fallback to serialized handling for hottest keys.

### 5. Where does queue-based serialization fit?
**A**: For extreme hotspot resources where correctness is strict and per-key deterministic ordering is required.

### 6. How do you reason about distributed locks in interviews?
**A**: Use them sparingly for narrow cross-node critical sections with timeout, fencing/idempotency, and clear failure semantics.

## Advanced Questions

### 7. How do you choose between 2PC and saga?
**A**: Use 2PC only when strict atomic commit across participants is mandatory and latency/availability trade-offs are acceptable; otherwise use saga with compensations.

### 8. What metrics guide policy changes?
**A**: Conflict rate, lock wait time, retry success ratio, p95/p99 latency, and failure queue growth.

### 9. How do you explain deadlock handling?
**A**: Minimize lock scope, enforce lock ordering, set timeout, and fail/retry with bounded backoff.

## Rapid Follow-up Drill

1. How would you protect last-seat booking correctness?
2. What is your fallback when lock service is unavailable?
3. How do you keep throughput during flash-sale spikes?
4. Which API should expose idempotency key requirements?

---

### Auction-specific follow-up

Q: How do you avoid conflicting highest-bid writes?
A: Keep per-auction correctness boundaries explicit and combine idempotent bid tokens with key-scoped conflict handling.
