# LLD Solution: Distributed Counter

**Time Target:** 45 minutes

## 1. Concurrency Defense & Requirements
**Say:** "The core requirement is to track an aggregate sum in a highly concurrent, multi-threaded environment. A simple mutex or atomic integer is insufficient because, under heavy load, cache invalidation and bus contention will cause throughput to plummet. My goal is to build a Striped Counter that disperses contention across an array of cells, dynamically resizing based on load to scale near-linearly with the number of CPU cores."

## 2. Data Structure Rationale
**Say:** "I will use a tiered approach:
1. **Base Value:** For low contention, all threads attempt to update a single `base` value using an atomic Check-and-Set (CAS) loop.
2. **Striped Cells:** If CAS on the `base` fails, we detect contention and allocate a `cells` array. Threads will route to specific cells based on a bit-mixed hash of their Thread ID.
3. **CellsBusy Lock:** A dedicated spin-lock will guard the array allocation and resizing phases to prevent race conditions during structural modifications."

## 3. Failure Handling & Race Conditions
**Say:** "To handle concurrent modifications to the array structure, any thread that detects a full array or contention on its assigned cell will attempt to acquire the `cellsBusy` lock. If successful, it doubles the array size and copies references. If unsuccessful, it rehashes its thread probe and tries another cell. This prevents 'lost updates' while avoiding deadlocks. To prevent infinite loops, the array size is capped at the number of available CPU cores—beyond that, more cells won't reduce contention because there aren't enough cores to execute threads simultaneously."

## 4. Production Trade-offs & Production Readiness
**Say:** "There are two major trade-offs in this design:
1. **Consistency of `get()`:** The read operation iterates over all cells to aggregate the sum. Because it doesn't freeze the entire system, concurrent increments can happen during the read. This means `get()` provides an eventually consistent, slightly stale snapshot.
2. **False Sharing:** In a high-performance system, packing `Cell` objects tightly in memory can cause multiple cells to land on the same 64-byte CPU cache line. When one thread updates its cell, the CPU invalidates the entire cache line for other cores, causing cache misses. In Java, I would mitigate this by annotating the `Cell` class with `@Contended` to pad the memory layout."

## 5. Walkthrough of the State Transition
**Say:** "Let's trace a thread:
1. The thread calls `increment(1)`.
2. It attempts `tryLock` on the `baseLock`. If successful, it increments `base` and returns.
3. If it fails, contention is detected. The thread checks if the `cells` array exists.
4. If not, it attempts to acquire `cellsBusy` to initialize an array of size 2.
5. Once the array exists, the thread hashes its ID to find an index, e.g., index 1.
6. It attempts `tryLock` on `cells[1]`. If successful, it increments and returns.
7. If that fails, it checks if `cells.length < NCPU`. If so, it acquires `cellsBusy` to double the array size to 4, then rehashes.
8. If the array is maxed out, it simply rehashes its ID to try a different cell, eventually succeeding."
