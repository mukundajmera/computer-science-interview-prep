# 🧭 Coding Pattern to System Design Map

A practical bridge from coding-round patterns to the system-design decisions where the same invariants reappear.

The goal is not to force coding tricks into architecture. The goal is to recognize when an algorithmic invariant becomes a production design lever: bounded memory, monotonic progress, ordered lookup, fairness, freshness, deduplication, or graph reachability.

---

## How to Use This Map

1. **Start from the coding invariant.** Know what the pattern proves locally.
2. **Translate the invariant into a system concern.** Ask whether the system needs ordering, bounded state, ranking, reachability, deduplication, or optimization.
3. **Name the production trade-off.** Strong interview answers explain why a simpler architecture is not enough, not just which data structure appears.
4. **Tie to repo examples.** Use the related content to practice the same idea in LLD, HLD, and operational terms.

---

## Core Transfer Table

| Coding Pattern | System Design Use | Related Repo Content | Interview Signal |
|---|---|---|---|
| [Two Pointers](./two-pointers/README.md) | Merge, scan, compact, dedupe, and reconcile ordered streams or bounded lists. | [Common Complexities](../00-theory/complexity-analysis/common-complexities.md), [Payment System](../04-hld-projects/payment-system/), [Ad Click Aggregator](../04-hld-projects/ad-click-aggregator/) | Explains monotonic progress, one-pass reconciliation, and why each item is processed once. |
| [Sliding Window](./sliding-window/README.md) | Maintain bounded recent history for rate limits, rolling metrics, alerting, and stream aggregation. | [LLD Rate Limiter](../02-lld-projects/rate-limiter/), [HLD Rate Limiting](../03-hld-concepts/rate-limiting/THEORY.md), [Stream Processing](../03-hld-concepts/stream-processing/THEORY.md), [Realtime Metrics Platform](../04-hld-projects/realtime-metrics-platform/) | Separates exact logs from bucketed approximations and defends memory/freshness trade-offs. |
| [Binary Search](./binary-search/README.md) | Find boundaries in ordered indexes, token rings, time ranges, cursor pages, and capacity thresholds. | [Indexing Strategies](../00-theory/database-concepts/indexing.md), [Consistent Hashing](../03-hld-concepts/consistent-hashing/THEORY.md), [Search Systems](../03-hld-concepts/search-systems/THEORY.md), [Load Balancing](../03-hld-concepts/load-balancing/THEORY.md) | Proves monotonic predicates before searching and states predicate cost, not only `O(log n)`. |
| [Heap / Priority Queue](./heap-priority-queue/README.md) | Serve top-K, ranking, scheduling, deadline ordering, and merge-K streams without sorting everything. | [Complexity Reference](../00-theory/cheat-sheets/complexity-reference.md), [YouTube Top K LLD](../02-lld-projects/youtube-top-k/), [News Feed](../04-hld-projects/news-feed/), [Video Recommendations](../04-hld-projects/video-recommendations/), [Job Scheduler](../04-hld-projects/job-scheduler/) | Chooses bounded heap vs full sort and explains latency, memory, freshness, tie-breaking, and stale-entry implications. |
| [BFS / DFS](./bfs-dfs/README.md) | Traverse social graphs, crawl frontiers, dependency DAGs, workflow graphs, and reachability boundaries. | [Common Complexities](../00-theory/complexity-analysis/common-complexities.md), [LinkedIn Connection LLD](../02-lld-projects/linkedin-connection/), [Web Crawler](../04-hld-projects/web-crawler/), [Workflow Orchestration](../03-hld-concepts/workflow-orchestration/THEORY.md) | States visited-set scope, frontier growth risk, cycle handling, and when bidirectional search helps. |
| [Dynamic Programming](./dynamic-programming/README.md) | Model staged optimization when local decisions depend on previous state: budget allocation, retry policy, batching, routing, or cost/latency trade-offs. | [Big-O Notation](../00-theory/complexity-analysis/big-o-notation.md), [Job Scheduler](../04-hld-projects/job-scheduler/), [Token / Cost / Latency Planning](../06-genai-systems/00-concepts/token-cost-latency/README.md) | Defines state, transition, and objective instead of hand-waving "optimize later." |
| [Greedy](./greedy/README.md) | Pick locally best candidates for scheduling, cache eviction, load assignment, pricing windows, and fallback order when the optimal global search is too slow. | [Caching](../03-hld-concepts/caching/THEORY.md), [Load Balancing](../03-hld-concepts/load-balancing/THEORY.md), [Price Tracking Service](../04-hld-projects/price-tracking-service/), [Quick Commerce Delivery](../04-hld-projects/quick-commerce-delivery/) | Names the exchange argument or admits heuristic risk with monitoring and rollback. |
| [Backtracking / Constraint Search](./backtracking/README.md) | Explore feasible allocations for seats, rooms, auctions, policy rules, or planner choices when constraints are tight and pruning matters. | [Movie Ticket Booking LLD](../02-lld-projects/movie-ticket-booking/), [Hotel Reservation LLD](../02-lld-projects/hotel-reservation/), [Online Auction](../04-hld-projects/online-auction/), [Ticketing Platform](../04-hld-projects/ticketing-platform/) | Describes pruning, duplicate suppression, timeout, fallback behavior, and why exhaustive search is contained. |
| [Trie / Prefix Index](./trie/README.md) | Power autocomplete, command lookup, path routing, prefix filtering, and search suggestions. | [Complexity Reference](../00-theory/cheat-sheets/complexity-reference.md), [Search Systems](../03-hld-concepts/search-systems/THEORY.md), [Elasticsearch](../03-hld-concepts/elasticsearch/THEORY.md), [Social Post Search](../04-hld-projects/social-post-search/) | Distinguishes prefix lookup from full-text relevance and explains memory vs latency. |
| [Union-Find](./union-find/README.md) | Track dynamic connectivity, clustering, duplicate groups, identity merges, and graph components. | [Common Complexities](../00-theory/complexity-analysis/common-complexities.md), [LinkedIn Connection LLD](../02-lld-projects/linkedin-connection/), [Distributed Coordination](../03-hld-concepts/distributed-coordination/THEORY.md), [Bot Detection Platform](../04-hld-projects/bot-detection-platform/) | Explains fast union/find for offline or batch grouping and when online graph queries need more. |
| Bloom Filter | Avoid expensive lookups for likely-absent items in crawlers, caches, storage systems, dedupe paths, and replay protection. | [Big Data Structures](../00-theory/big-data-structures/README.md), [Caching](../03-hld-concepts/caching/THEORY.md), [Web Crawler](../04-hld-projects/web-crawler/), [File Storage](../04-hld-projects/file-storage/) | States false-positive behavior and never treats probabilistic membership as proof of existence. |
| Consistent Hashing | Map keys to shards, cache nodes, replicas, and ownership ranges while minimizing movement on membership changes. | [Consistent Hashing](../03-hld-concepts/consistent-hashing/THEORY.md), [Distributed Cache](../04-hld-projects/distributed-cache/), [Database Sharding](../03-hld-concepts/database-sharding/THEORY.md), [Load Balancing](../03-hld-concepts/load-balancing/THEORY.md) | Connects ring lookup to binary search and explains rebalancing, virtual nodes, hot keys, and replication. |

---

## Pattern Selection by System Signal

| System Signal | Pattern Lens | Strong Follow-Up |
|---|---|---|
| "last N seconds", "rolling p95", "requests per minute" | Sliding window | Exact log vs bucketed counter vs stream window state. |
| "top K", "highest score", "next job by priority" | Heap / priority queue | Bounded heap, freshness, stale entries, tie-breaking, and shard-local vs global top-K. |
| "first item after cursor", "next ring token", "minimum capacity that passes" | Binary search | Predicate monotonicity, index freshness, and cost of each check. |
| "shortest connection", "crawl frontier", "dependency graph" | BFS / DFS | Frontier explosion, visited-set storage, cycle handling, and bounded depth. |
| "all valid assignments", "constraint grid", "choose or skip" | Backtracking | Pruning, duplicate suppression, recursion depth, timeout, and fallback strategy. |
| "autocomplete", "prefix route", "typeahead" | Trie / prefix index | Prefix-only lookup vs relevance ranking and memory compression. |
| "dedupe before expensive fetch", "probably seen" | Bloom filter | False positives, no false negatives, and authoritative fallback store. |
| "dynamic clusters", "same component", "identity merge" | Union-find | Batch connectivity vs online graph queries. |
| "local best is good enough under latency" | Greedy | Correctness proof if exact; observability and rollback if heuristic. |

---

## Interview Transfer Prompts

Use these prompts to turn a coding answer into a system-design answer:

1. **Invariant:** What fact is preserved as the algorithm runs?
2. **Production boundary:** What system boundary preserves the same fact: index, queue, cache, shard, window, or graph frontier?
3. **Failure mode:** What breaks when scale, concurrency, staleness, or partial failure enters?
4. **Trade-off:** What do we buy with this pattern, and what do we give up?
5. **Validation:** What metric proves the production version is working?

---

## Common Mistakes

1. Saying "use a heap" when the real problem is stale ranking or distributed merge.
2. Saying "use sliding window" without memory bounds or late-event handling.
3. Saying "binary search is O(log n)" when the feasibility check scans a fleet, shard, or dataset.
4. Treating Bloom filters, search indexes, caches, or ML scores as sources of truth.
5. Ignoring hot keys, skew, duplicate events, and retries when translating clean coding inputs to production systems.

---

## Study Path

1. Complete the live packs: [Two Pointers](./two-pointers/README.md), [Sliding Window](./sliding-window/README.md), [Binary Search](./binary-search/README.md), [BFS/DFS](./bfs-dfs/README.md), [Dynamic Programming](./dynamic-programming/README.md), and [Greedy](./greedy/README.md).
2. Add the branching, ranking, prefix-index, and connectivity packs: [Backtracking](./backtracking/README.md), [Heap / Priority Queue](./heap-priority-queue/README.md), [Trie](./trie/README.md), and [Union-Find](./union-find/README.md).
3. For each row above, open the related LLD or HLD project and identify where the same invariant appears.
4. Practice a 60-second transfer explanation:
   - "The coding invariant is..."
   - "The production component that preserves it is..."
   - "The scale risk is..."
   - "The validation metric is..."
5. Revisit this map whenever a new coding pack is added so the transfer layer stays current.
