# Approach

## Overview
A naive implementation of a counter uses a single lock or a single atomic variable (e.g., `AtomicLong`). While this ensures correctness, it becomes a severe bottleneck under high concurrency since every thread competes for the same memory location, leading to cache invalidation and bus contention.

To solve this, we use a technique called **Striping**. We distribute the counter value across an array of `Cell` objects. *Note: LongAdder/striped local state is not a network-distributed counter, and a concurrent sum is not an atomic snapshot suitable for strict quota limits.*

## Versions

### v1-basic
- **Design:** Uses a single long value protected by a mutex/synchronized block.
- **Pros:** Simple, exact, uses minimal memory, provides an atomic snapshot suitable for strict quota decisions.
- **Cons:** Heavy contention. Threads serialize at the lock, devastating throughput.

### v2-extended
- **Design:** Uses a fixed-size array of `Cell` objects. Each cell contains a partial sum and is protected by its own lock.
- **Routing:** Threads are routed to cells using their `Thread ID % NUM_CELLS`.
- **Pros:** Reduces contention by a factor of `NUM_CELLS`.
- **Cons:** If `NUM_CELLS` is too small, contention remains. If too large, we waste memory. Additionally, if multiple active threads hash to the same cell, they still contend, and the concurrent sum requires aggregating across cells, resulting in a non-atomic snapshot unsuitable for strict quota limits.

### v3-optimized
- **Design:** Implements dynamic resizing and contention detection, similar to Java's `LongAdder`.
- **Mechanics:**
  - Starts with a single `base` value.
  - If a thread fails to update the `base` without contention (e.g., `tryLock` fails), it allocates an array of `Cell` objects.
  - Threads map to cells using a pseudo-random thread probe hash.
  - If contention is detected on a specific cell, the system attempts to resize the array (up to the number of available CPUs) and rehashes the thread's probe.
- **Pros:** scales near-linearly with the number of CPU cores. Zero array overhead under low contention.
- **Cons:** `get()` requires summing all cells, meaning it provides a slightly stale read if concurrent updates happen during the summation.
