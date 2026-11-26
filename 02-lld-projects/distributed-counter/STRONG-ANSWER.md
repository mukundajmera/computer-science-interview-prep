# Strong Answer

**Time Target:** 45 minutes

## 1. Concurrency Defense & Requirements (0-10 min)
**Say:** "The core requirement is to track an aggregate sum in a highly concurrent, multi-threaded environment. I will start with a baseline locked counter (like `AtomicLong` or a single Mutex). However, under heavy load, cache invalidation and bus contention will cause throughput to plummet. My goal is to build a Striped Counter that shards contention across an array of cells in local memory, dynamically resizing based on load to scale near-linearly with the number of CPU cores."

## 2. Data Structure Rationale (10-20 min)
**Say:** "I will use a tiered approach:
1. **Base Value:** For low contention, all threads attempt to update a single `base` value using an atomic Check-and-Set (CAS) loop.
2. **Striped Cells:** If CAS on the `base` fails, we detect contention and allocate a `cells` array. Threads will route to specific cells based on a bit-mixed hash of their Thread ID.
3. **CellsBusy Lock:** A dedicated spin-lock will guard the array allocation and resizing phases to prevent race conditions during structural modifications."

## 3. Failure Handling & Correctness Invariants (20-30 min)
**Say:** "To handle concurrent modifications to the array structure, any thread that detects a full array or contention on its assigned cell will attempt to acquire the `cellsBusy` lock. To prevent a resizing race condition, the thread must verify that the array hasn't already been resized by another thread while it was waiting for the lock.
The core **correctness invariant** is that the total sum of `base` plus all active `Cell` values exactly equals the total increments applied. Space complexity is O(N) where N is the number of cells (capped at CPU cores), and Time complexity is O(1) for increment, but O(N) for `get()`."

## 4. Production Trade-offs (30-40 min)
**Say:** "There are two major trade-offs in this design:
1. **Consistency of `get()`:** The read operation iterates over all cells to aggregate the sum. It does not freeze the entire system, meaning a concurrent sum is an interleaved state, not an atomic snapshot. Therefore, this counter is excellent for metrics but **not suitable for strict quota limits**.
2. **False Sharing:** Packing `Cell` objects tightly in memory can cause them to land on the same 64-byte CPU cache line. I would mitigate this by padding the memory layout (e.g., `@Contended` in Java)."

## 5. Staff Follow-Up (40-45 min)
**Say:** "While the problem is often called a 'distributed counter', it is important to clarify that this is a single-node thread-safe counter. If we needed a true network distributed counter, we would use CRDTs or a consensus system, which introduces completely different latency and partition tolerance trade-offs."
