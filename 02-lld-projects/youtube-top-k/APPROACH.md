# Approach for YouTube Top K

## Overview and Core Strategy
The "YouTube Top K" problem involves determining the most frequently viewed videos (the Top K heavy hitters) over a specific time window, out of billions of daily view events. The core challenge is that maintaining an exact count of every single video ID in memory and sorting them is computationally and spatially impossible at scale.

Our approach abandons exact precision in favor of highly accurate approximation algorithms. We utilize a distributed, stream-processing architecture heavily reliant on the Count-Min Sketch data structure and partitioned Min-Heaps to process unbounded data streams with bounded memory.

## Approximate Counting (Count-Min Sketch)
To count views without storing every video ID, we approach the problem using a Count-Min Sketch (CMS).
- A CMS is a probabilistic data structure consisting of a 2D array of counters and multiple independent hash functions. In our `v2-extended` and `v3-optimized` versions, we use deterministic hashes (e.g., MD5 seeded by depth) and configure the CMS with `width = 1000` and `depth = 5`. This yields a specific error probability bounded by `1 - e^(-depth)`.
- When a view event for `Video_A` arrives, we hash `Video_A` using the functions to find specific indices in the 2D array and increment those counters.
- To query the count for `Video_A`, we hash it again, look at the corresponding counters, and return the minimum value. 
- Count-Min estimates never undercount valid nonnegative updates. Any negative view counts are strictly ignored to maintain this invariant.
- **The Benefit:** This requires a tiny, fixed amount of memory (e.g., a few megabytes) regardless of whether there are 1 million or 1 billion unique videos.
- **The Trade-off:** It can overestimate counts (due to hash collisions), but it never underestimates. For finding the *Top* K, overestimation of small videos is statistically insignificant, making it an ideal trade-off.

## Distributed Top-K Maintenance
A single CMS cannot handle global traffic. We approach this using data partitioning.
- Incoming view events are partitioned by `Video_ID` (using consistent hashing) across a cluster of Aggregator Nodes.
- Each Aggregator Node maintains its own local Count-Min Sketch and a local Min-Heap of size K (bounded memory). 
- Top-k candidate eviction works by tracking candidates in a size K Min-Heap: as the CMS is updated, if the new estimated count for a video exceeds the smallest count in the Min-Heap, the video is inserted into the heap (and the smallest is evicted). Ties are deterministically broken by ascending video ID.
- Behavior under empty stream, window rotation, and exact counts for Top K candidates are rigorously validated by comparing them with an exact small reference stream.
- To find the global Top K, a central Query Node requests the local Top K from every Aggregator Node, merges them into a final Min-Heap, and returns the result.

## Time Windowing and Versions
To calculate Top K for the "last 24 hours," we utilize a Tumbling Window approach comprised of discrete time buckets (e.g., 1-hour buckets). As time progresses, window rotation discards the oldest buckets from active memory when a node tracks more than a configured limit, while preserving them in persistent storage. 

Our implementation spans three actual supported versions:
- `v1-basic`: An in-memory baseline that provides simple `recordView` and `getTopK` relying on basic unbounded maps.
- `v2-extended`: Introduces the probabilistic Count-Min Sketch, bounded Min-Heap for real-time tracking, and Tumbling Window rotation with `WindowStateStore` abstraction.
- `v3-optimized`: Adds idempotency with `IdempotencyStore` for deduplication and a `DistributedRepository` to handle cross-region state persistence.
