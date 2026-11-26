# Contention Control

Contention control manages concurrent operations targeting the same scarce resource without breaking correctness or throughput.

## What is it?

It is the set of concurrency strategies used to prevent race conditions, double-booking, and inconsistent updates under concurrent access.

## Why do we need it?

- Hot resources create conflicting writes.
- Naive read-then-write logic oversells inventory and duplicates reservations.
- Strong correctness and high throughput require explicit coordination choices.

## Types/Approaches

### 1. Single-Node Controls
- Transaction + row lock (`SELECT ... FOR UPDATE`).
- Optimistic concurrency control (version check + retry).
- Isolation level tuning for conflict semantics.

### 2. Multi-Node Controls
- Distributed lock for short critical sections.
- Queue-based serialization for hot keys.
- Saga/compensation when atomic global commit is impractical.

### 3. Escalation Ladder
- Start with optimistic control.
- Escalate to pessimistic lock if conflict rate rises.
- Serialize only the hottest keys.
- Add distributed coordination only when single-node guarantees are exhausted.

### The Stale Lock Holder Problem (Paused Owner Trace)

A common pitfall in multi-node coordination is assuming that a [distributed lock](../zookeeper/THEORY.md) strictly prevents concurrent writes. It does not. If a process experiences a severe pause, its lock lease can expire, allowing another process to acquire the lock. When the original process resumes, it still believes it holds the lock and proceeds to write, causing corruption.

**Paused Owner Trace:**
1.  **Time 1**: Process A (Client 1) acquires a distributed lock (epoch = 7).
2.  **Time 2**: Process A experiences a severe Garbage Collection (GC) pause or network partition.
3.  **Time 3**: The lock manager (e.g., ZooKeeper) detects a session timeout and expires Process A's lease.
4.  **Time 4**: Process B (Client 2) acquires the distributed lock (epoch = 8).
5.  **Time 5**: Process B writes to the database successfully and releases the lock.
6.  **Time 6**: Process A's GC pause ends. Unaware that its lease expired, it proceeds with its write, overwriting Process B's changes.

### Distributed Mutual Exclusion vs Fencing vs Idempotency
- **Distributed Mutual Exclusion (Locks)**: Attempts to prevent two nodes from doing the same work simultaneously to save resources. It relies on time and leased sessions, making it vulnerable to the paused owner problem.
- **Fencing**: Guarantees strict ordering and prevents stale writes by having the *storage authority* validate a monotonic token (epoch) on every mutation.
- **Idempotency**: Ensures that applying the same valid operation multiple times has the same effect as applying it once. It does not natively prevent the stale interleaving of different operations.

### Fencing Tokens

To solve the stale lock holder problem, the system must use **fencing tokens**. A fencing token is a monotonically increasing number (epoch) granted by the lock manager every time a lock is acquired. 

The *storage authority* (e.g., a database) must validate this token on every mutation. It records the highest token it has ever seen and explicitly rejects any write carrying a token less than or equal to the highest seen.

**Fencing Trace (Success):**
1.  **Time 1**: Process A acquires lock, gets fencing token `epoch=7`.
2.  **Time 2**: Process A pauses; lease expires.
3.  **Time 3**: Process B acquires lock, gets fencing token `epoch=8`.
4.  **Time 4**: Process B writes to storage with `epoch=8`. Storage accepts and records highest seen as 8.
5.  **Time 5**: Process A resumes and attempts to write to storage with `epoch=7`.
6.  **Time 6**: Storage explicitly rejects Process A's write because `7 <= 8`. 

#### Single-Node SQL Alternative
For simple workloads, a database can handle contention natively using an optimistic version check, avoiding external coordination entirely:
```sql
UPDATE inventory 
SET stock = stock - 1, version = 8 
WHERE item_id = 123 AND version = 7;
```
If `version` was incremented by another process while the client paused, no rows are updated, and the client must retry.


## How it works

1. Identify resource key and correctness boundary.
2. Choose policy by conflict frequency and latency budget.
3. Execute operation under chosen policy.
4. Retry/compensate/route-to-queue on conflict.
5. Emit metrics to tune policy thresholds.

## When to use

- Inventory reservation, seat booking, coupon claims, account transfers, matching assignments.

## When NOT to use

- Low-conflict, append-only workloads where coordination overhead is unnecessary.

## Trade-offs

| Strategy | Strength | Weakness |
|---|---|---|
| Optimistic | High throughput under low conflict | Retry storms at high contention |
| Pessimistic | Strong correctness with simple reasoning | Lock waits/deadlock risk |
| Serialized queue | Deterministic per-key order | Throughput bottleneck per key |
| Distributed lock | Cross-node mutual exclusion | Availability/timeout complexity |

## Requirements and constraints

- Define idempotency guarantees before retrying.
- Set contention thresholds and backoff policy.
- Keep lock scope minimal and timeout bounded.
- Separate transient conflict from permanent business failure.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|---|---|---|
| Policy choice | Chosen by measured conflict profile | One-size-fits-all locking |
| Correctness | Explicit resource key and invariants | Vague consistency claims |
| Failure handling | Retry, timeout, compensation explained | No conflict failure path |
| Scalability | Escalation path from v1 to v3 | Premature distributed locks |

## Common pitfalls

- Using distributed locks when DB transaction is enough.
- Ignoring idempotency during retry loops.
- Unbounded retries under sustained hotspots.
- No deadlock/timeout handling policy.

## Follow-up questions

1. What conflict rate triggers policy escalation?
2. How do you prevent retry storms?
3. Which operations must fail closed vs degrade?
4. How do you test correctness under concurrent load?
5. Where would you add queue-based serialization?

## Variants and extensions

- Per-key adaptive contention policy.
- Token-based reservation windows.
- CRDT/eventual model for non-critical counters.
- Regional ownership + async reconciliation.

## Related concepts

- [CAP Theorem](../cap-theorem/THEORY.md)
- [Distributed Transactions](../distributed-transactions/THEORY.md)
- [Pattern Selection for HLD Interviews](../pattern-selection/THEORY.md)
- [E-commerce Backend HLD](../../04-hld-projects/ecommerce-backend/)
- [Ride Sharing HLD](../../04-hld-projects/ride-sharing/)

---

## Source 13 Integration: Auction Contention Scenario

Use auction bidding as the canonical high-conflict example: monotonic bid updates require strict correctness per auction key, bounded retries, and explicit escalation from optimistic checks to key-level serialization when contention spikes.
