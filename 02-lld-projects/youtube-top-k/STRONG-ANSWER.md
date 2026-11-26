# Strong Answer: YouTube Top-K Trending Videos

**Pacing Target:** 45 minutes

## 1. Introduction & Version Roadmap (0-5 minutes)

**Say:** "To design the YouTube Top-K Trending Videos, I'll start with an in-memory proof-of-concept and iteratively scale it to a distributed-friendly architecture. Our roadmap is:
- **v1-basic:** In-memory baseline focusing on core aggregation logic without windowing.
- **v2-extended:** Introduction of tumbling time windows, bounded probabilistic structures (Count-Min Sketch), and strict interface boundaries (`WindowedTopKAggregator`, `TopKQueryService`, `WindowStateStore`).
- **v3-optimized:** Distributed-friendly interfaces with idempotency hooks (`IdempotencyStore`) to prevent double-counting during at-least-once processing retries, and a `DistributedRepository` for state checkpointing."

## 2. Approximate Counting with Count-Min Sketch (5-15 minutes)

**Say:** "Maintaining an exact count of every single video ID in memory is spatially impossible at scale. We use a **Count-Min Sketch (CMS)**, a probabilistic data structure. By default, it's defined with a deterministic `width = 1000` and `depth = 5`. It trades precision for O(1) memory bound per key. Its error probability depends on the width and stream size, with certainty bounded by `1 - e^(-depth)`."

Crucially, **Count-Min estimates never undercount valid nonnegative updates**. It uses deterministic hashing (e.g., MD5 seeded differently for each depth level). When a view event arrives, it maps hashes to indices and increments the counters. Because it only increments on valid view events, the minimum across all depth buckets guarantees no undercounting, though collisions can cause overestimation.

## 3. Top-K Bounded Memory and Candidate Eviction (15-25 minutes)

**Say:** "Alongside the CMS, we maintain a Bounded Min-Heap of size exactly `K`. When an event updates the CMS, we get the new estimated count. If this count exceeds the smallest count in our heap (the root), we have a candidate for the top K. If it's already in the heap, we update its count. Otherwise, we evict the root (the lowest count) and insert the new candidate, taking `O(log K)` time."

We use lock-free updates (like `AtomicIntegerArray` or `LongAdder`) for the heavily contended CMS array to maximize throughput, while the much smaller heap uses standard synchronization (e.g., `ReentrantReadWriteLock`).

## 4. Worked Example: Probabilistic vs Exact Reference Stream (25-35 minutes)

Let's trace a concrete example comparing the probabilistic structures to an exact reference stream, handling top-K candidate eviction, ties, window rotation, and empty streams.

**Reference Stream (Window Size = 1 hour, K = 2, CMS width = 5, depth = 3):**
- Window 0 (00:00 - 01:00): `[(v1, t=10), (v1, t=20), (v2, t=30), (v3, t=40), (v1, t=50), (v2, t=60), (v4, t=70), (v1, t=80)]`
- Window 1 (01:00 - 02:00): Empty stream
- Window 2 (02:00 - 03:00): `[(v5, t=7200010)]`

**Processing Window 0:**
1. `v1` arrives. CMS estimate for `v1` becomes 1. Heap: `[(1, v1)]`
2. `v1` arrives. CMS=2. Heap updates: `[(2, v1)]`
3. `v2` arrives. CMS=1. Heap: `[(1, v2), (2, v1)]` (min is at root)
4. `v3` arrives. CMS=1. **Tie Case:** Heap root is `(1, v2)`. Since the estimate (1) is not strictly greater than the root count (1), `v3` does not evict `v2`. Ties favor the incumbent. Heap remains: `[(1, v2), (2, v1)]`
5. `v1` arrives. CMS=3. Heap updates: `[(1, v2), (3, v1)]`
6. `v2` arrives. CMS=2. Heap updates: `[(2, v2), (3, v1)]`
7. `v4` arrives. CMS=1. **Candidate Eviction Miss:** Estimate (1) is less than root (2). Heap remains unchanged.
8. `v1` arrives. CMS=4. Heap updates: `[(2, v2), (4, v1)]`

Top 2 query result for Window 0: `[v1, v2]`.

**Window 1 (Empty Stream):**
No events arrive. A Top-K query for this window gracefully falls back to the persistent store (which is empty) and returns an empty list `[]`, avoiding null pointer exceptions.

**Window 2 (Window Rotation):**
Event `(v5, t=7200010)` arrives. The timestamp falls into Window 2. A fresh, independent `WindowState` (new CMS + empty Heap) is initialized. `v5` is inserted. Old windows remain intact in memory (until eviction maximum) and storage.

## 5. Distributed Architecture & Synchronization (35-45 minutes)

**Say:** "To scale to YouTube's traffic, we partition incoming view events by `Video_ID` across a Kafka cluster into Aggregator Nodes. Each node maintains its local CMS and Min-Heap. A central Query Node handles API requests, executing a scatter-gather operation to fetch local Top-K lists from all aggregators, merge them, and return the definitive global Top-K."

In `v3-optimized`, we ensure idempotency. If a Kafka partition rebalances, events might be replayed. The `IdempotencyStore` claims and deduplicates view events with a TTL, guaranteeing that our Count-Min Sketch estimates are not artificially inflated by stream processing retries.
