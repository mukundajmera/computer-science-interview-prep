# Pitfalls

## 1. Non-Atomic Snapshot (`get()` method)
A common mistake is treating the concurrent sum returned by `get()` as an atomic snapshot.
**Failure Trace:** Thread A calls `get()`. It reads cell 0 (value=10). Thread B increments cell 1 (value goes 0->1). Thread A reads cell 1 (value=1). The sum returned is 11. Thread A thinks 11 was a precise state at a single moment, but it's an interleaved state. This is not suitable for strict quota limits (e.g., denying an API request exactly at the 1000th call).

## 2. Lost Updates
If atomic operations (CAS) or locks are not correctly used when updating a `Cell` or the `base` value, concurrent threads might read the same old value, increment it, and overwrite each other.

## 3. False Sharing
If `Cell` objects are packed tightly in memory, they might reside on the same CPU cache line (typically 64 bytes). When different CPUs update different cells on the same cache line, the entire cache line is invalidated across CPUs, severely degrading performance.

## 4. Array Resizing Race Conditions
**Failure Trace:** Thread A and Thread B both detect contention on an array of size 2. Thread A acquires `cellsBusy`, doubles the array to 4, copies cells, and releases the lock. Thread B then acquires `cellsBusy` but fails to check if the array was *already* resized. It allocates another array of size 4, overwriting Thread A's array. Any increments applied to Thread A's array are orphaned and lost.

## 5. Endless Loops
In the `v3-optimized` loop, if the retry logic does not properly advance the thread probe or yield, a thread might get stuck endlessly spinning on a contended cell, burning CPU without making progress.
