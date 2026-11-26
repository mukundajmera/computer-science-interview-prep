# Rubric

## 1. Concurrency Handling (40%)
- **L4 (Intuitive minimum example):** The candidate correctly implements the `v1-basic` locked baseline (e.g., using `AtomicLong` or `synchronized`/`Lock`), understanding why a simple non-atomic sum fails in a multi-threaded application.
- **L5 (Trade-offs):** The candidate identifies the lock contention bottleneck and implements Striping (array of cells). They can explain how sharding changes the baseline locking model.
- **L6/L7 (Failure trace & Assumptions):** The candidate correctly simulates contention detection, thread probe hashing, and safe dynamic array resizing. They can trace a failure where a concurrent `get()` sum is mistakenly treated as an atomic snapshot.

## 2. Dynamic Resizing & Memory Efficiency (20%)
- **L5:** Does the array size cap out at the number of available CPUs?
- **L6:** Do they lazily allocate cells instead of allocating them all upfront to avoid unnecessary memory overhead?

## 3. Correctness Invariants (20%)
- **L4:** Does `get()` accurately sum the values without throwing exceptions?
- **L6/L7:** Are variables `volatile` or protected by locks to ensure visibility? The candidate explains that the sum of `base` plus all active `Cell` values must exactly equal the total applied increments, provided no operations are lost due to a resizing race condition.

## 4. Code Quality & Modularity (20%)
- **L4:** Code is clean and small.
- **L5:** The thread probe hashing and resize lock logic are separated from the core increment flow.
