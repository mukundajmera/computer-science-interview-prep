# Follow-Ups

## 1. Optional Staff Follow-up: Distributed Counters vs Local Striped Counters
**Question:** The system we built is a single-node thread-safe counter. How does this compare to a true distributed system counter (e.g., Redis)?
**Answer:** A local striped counter (like `LongAdder`) handles multi-core concurrency using shared memory. A true distributed counter must handle network partitions and node failures. In a distributed system, we would need a consensus algorithm or use CRDTs (Conflict-free Replicated Data Types) like a PN-Counter to aggregate values across separate network nodes asynchronously. The term "sharding" here applies to memory addresses, not network hosts.

## 2. Optional Staff Follow-up: Enforcing Strict Quotas
**Question:** You mentioned the `get()` method is not an atomic snapshot. How would you design a system to enforce strict API quota limits?
**Answer:** Because `get()` aggregates sequentially, you cannot use it to strictly deny exactly the N+1th request without race conditions. To enforce a strict quota, you must serialize the limit check and the increment (e.g., using a single global lock or a single atomic `compareAndSet` loop), which sacrifices the throughput gained by striping. Alternatively, a token bucket algorithm can be used for rate limiting.

## 3. How would you prevent False Sharing?
**Answer:** Pad the `Cell` class so that each instance is at least 64 bytes. In Java, this can be done using the `@Contended` annotation or manually adding dummy `long` fields.

## 4. What if we want a `decrement` operation?
**Answer:** The exact same logic applies. `decrement(x)` is simply `increment(-x)`. Since addition and subtraction commute, the striped approach handles it perfectly.
