# Code Walkthrough

This document describes the actual merged code and tests for the counter. The system is a single-node thread-safe counter (often using a `LongAdder`-style striped local state), not a true distributed counter across a network. It focuses on how sharding changes the baseline locking model.

## Entry APIs
- `increment(x)`: Adds `x` to the counter. Route threads to specific cells to minimize lock contention.
- `get()`: Retrieves the aggregate sum. Note: A concurrent sum is not an atomic snapshot and is not suitable for strict quota limits.

## Version Delta Table

| Version | Description | Complexity | Trade-offs |
|---------|-------------|------------|------------|
| **v1-basic** | Simple globally locked counter (AtomicLong / ReentrantLock baseline). | Time: O(1)<br>Space: O(1) | Strict serialization. High lock contention destroys throughput. |
| **v2-extended** | Fixed-size array of `Cell` objects (striped counter). | Time: O(1) increment, O(N) get<br>Space: O(N) | Reduces contention by N. Unused cells waste memory. |
| **v3-optimized** | Dynamically resizing array with contention detection and probe hashing. | Time: O(1) increment, O(N) get<br>Space: O(N) | Scales near-linearly with CPUs. Complex resize logic and false sharing risks. |

## Code Paths
## v1-basic
The basic implementation uses a single `synchronized` block or `ReentrantLock`. Any call to `increment()` or `get()` must acquire this lock, guaranteeing mutual exclusion. The result is total accuracy but strict serialization.

## v2-extended
We introduce a `Cell` class. The `Counter` maintains a fixed-size array of `Cell` objects.
When a thread calls `increment()`, we identify its thread ID, compute `threadId % cells.length`, and lock only that specific cell to add the value. When `get()` is called, we iterate over all cells, locking each one sequentially to accumulate the total. This disperses the load.

## v3-optimized
This version implements sophisticated concurrency control:
1. **Base Value:** Under no contention, threads update a single `base` value.
2. **Contention Detection:** If updating `base` fails (`tryLock` returns false), the thread experiences contention.
3. **Dynamic Allocation:** The counter allocates the `cells` array (starting at size 2).
4. **Thread Probes:** Instead of a simple thread ID modulo, we use an advanced bit-mixing function to generate a "probe". This hash determines the cell index.
5. **Resizing:** If a thread fails to acquire the lock for its assigned cell, it signals contention. The array doubles in size (up to `NCPU`) to spread threads further.
6. **Rehashing:** If the array is maxed out or a resize isn't appropriate, the thread's probe is rehashed using a XorShift algorithm to map it to a different cell.
7. **CellsBusy Lock:** A separate spin-lock (`cellsBusy`) protects the initialization and resizing of the `cells` array itself to ensure only one thread mutates the structure at a time.
