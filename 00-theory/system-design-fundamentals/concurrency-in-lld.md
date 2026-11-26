# Concurrency in LLD

Concurrency decisions in LLD interviews are rarely about raw thread APIs. They are about choosing the right ownership boundary and proving correctness under contention.

---

## Concurrency in LLD scope

In low-level design rounds, concurrency usually appears in three places:
- Shared mutable state (seat inventory, counters, balances, queue state)
- Multi-step workflows (lock -> validate -> commit)
- Time-bound ownership (TTL locks, retries, lease expiry)

The interview target is a design that is easy to reason about, not the most complex synchronization primitive.

---

## Correctness vs Coordination vs Scarcity

### Correctness
Question: "Can two concurrent operations violate a core invariant?"
- Example invariants: one seat cannot be sold twice, stock cannot go negative.
- Typical failure mode: check-then-act race.

### Coordination
Question: "How do producers and consumers hand off work safely?"
- Focus on ordering, bounded queues, retry behavior, and shutdown semantics.
- Typical failure mode: unbounded queues or unclear ownership transitions.

### Scarcity
Question: "How do we govern finite permits/resources fairly and safely?"
- Focus on tokens/permits, timeout policy, release safety, and starvation prevention.
- Typical failure mode: leaked permits or unbounded admission under spikes.

---

## Primitive toolbox and selection heuristics

| Primitive | Use when | Watch-outs |
|---|---|---|
| Mutex / monitor lock | Small critical section with shared in-memory state | Oversized lock scope hurts throughput |
| Read-write lock | Many readers, few writers, expensive write path | Writer starvation and upgrade complexity |
| Atomic CAS/versioning | Low-contention optimistic updates | Retry storms under heavy contention |
| Semaphore / permit gate | Capacity governance and backpressure | Permit leaks, unclear timeout/retry policy |
| Bounded queue | Producer-consumer handoff | Must define full-queue behavior |
| Condition/notify | State-change waiting in one process | Missed signals if predicate checks are sloppy |

Heuristic: start with the narrowest primitive that protects one explicit invariant, then scale only where evidence shows contention.

---

## Requirements and constraints

### Functional requirements
- Preserve domain invariants under concurrent access.
- Keep API outcomes deterministic for retriable calls.
- Define timeout and cancellation behavior for in-flight operations.

### Non-functional constraints
- Keep critical sections small and measurable.
- Avoid unbounded memory growth from coordination structures.
- Preserve language parity (Java/Python) in interview implementations.
- Keep designs testable without external infrastructure.

---

## Scoring rubric

| Dimension | Strong signal |
|---|---|
| Invariant clarity | Candidate states explicit invariant and ownership boundary |
| Atomicity design | Multi-step flows are guarded against races |
| Coordination policy | Queue/worker handoff and backpressure are explicit |
| Scarcity policy | Permit/token lifecycle is safe under timeout and failure |
| Communication | Trade-offs are framed with when/why, not buzzwords |

---

## Common pitfalls

- Treating thread safety as a final refactor rather than a first-order requirement.
- Splitting check and update across unguarded steps.
- Using distributed locks by default when local ownership is sufficient.
- Ignoring failure cleanup (expired lock, stuck permit, duplicate retry).
- Adding concurrency primitives without proving which invariant they protect.

---

## Follow-up questions

1. What exact invariant is protected by this lock/atomic operation?
2. What happens when two requests race on the same entity?
3. How does your design behave when queue/permit capacity is exhausted?
4. Which operation is safe to retry, and why?
5. What metric tells you the current strategy no longer scales?

---

## Variants and extensions

- Add weighted permits for expensive operations.
- Add lock lease renewal and expiry sweeper behavior.
- Add optimistic-first with pessimistic fallback policy.
- Add multi-node ownership with explicit fail-open/fail-closed modes.
- Add admission control by tenant or priority class.

---

## Cross-references

- [System Design Interview Delivery Framework](./system-design-interview-delivery-framework.md)
- [Synchronous vs Asynchronous](./sync-vs-async.md)
- [Movie Ticket Booking](../../02-lld-projects/movie-ticket-booking/)
- [Rate Limiter](../../02-lld-projects/rate-limiter/)
- [Job Scheduler](../../02-lld-projects/job-scheduler/)
- [LLD Checklist](../../resources/interview-tips/lld-checklist.md)
