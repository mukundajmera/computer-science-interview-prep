# Top Coding Practice Ladder

A prioritized, interview-oriented list drawn from the live coding pattern packs in this repository. It preserves the curated Top 20 sequence and adds Wave 3 extension rows for graph traversal, dynamic programming, greedy proof, backtracking, heap, trie, and Union-Find fundamentals.

Use this file as a sequencing guide, not as a replacement for the pattern pages. Every problem link points to an existing guided page with requirements, approach, scoring rubric, pitfalls, follow-ups, variants, and system-design cross-links.

## How to Use This List

1. **First pass:** solve each problem within the target time and write down the invariant before coding.
2. **Second pass:** explain the system-design transfer: what production component preserves the same invariant?
3. **Third pass:** practice the follow-up questions in the linked guided page.
4. **Elite pass:** compare two adjacent rows from the same pattern and explain why the template changes.

Difficulty here means interview-readiness difficulty for this curriculum. It is not a copy of any external platform label.

## Curated Top 20

| Rank | Problem Source | Pattern | Difficulty | Core Insight | Related Repo Content | Time Target |
|---|---|---|---|---|---|---|
| 1 | [Two Sum (Sorted Array)](./two-pointers/03-two-sum-sorted-array.md) | Two Pointers | Easy | Move the pointer that can still improve the sum; prove the discarded side cannot produce the target. | [Indexing](../00-theory/database-concepts/indexing.md) | 12 min |
| 2 | [Move Zeroes](./two-pointers/06-move-zeroes.md) | Two Pointers | Easy | Separate scan position from write position so stable compaction stays one pass and in place. | [Message Queues](../03-hld-concepts/message-queues/THEORY.md) | 12 min |
| 3 | [Container With Most Water](./two-pointers/02-container-with-most-water.md) | Two Pointers | Medium | Shrink the limiting boundary because keeping it cannot increase area. | [Load Balancing](../03-hld-concepts/load-balancing/THEORY.md) | 18 min |
| 4 | [3-Sum](./two-pointers/04-three-sum.md) | Two Pointers | Medium | Sort once, fix one value, then use duplicate-safe two-pointer search for the complement. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 25 min |
| 5 | [Valid Triangle Number](./two-pointers/05-valid-triangle-number.md) | Two Pointers | Medium | Sort and count many valid pairs at once instead of checking every triple. | [Complexity Reference](../00-theory/cheat-sheets/complexity-reference.md) | 22 min |
| 6 | [Sort Colors](./two-pointers/07-sort-colors.md) | Two Pointers | Medium | Maintain three regions and move each item into its final partition with constant memory. | [Content Moderation Platform](../04-hld-projects/content-moderation-platform/DESIGN.md) | 20 min |
| 7 | [Trapping Rain Water](./two-pointers/08-trapping-rain-water.md) | Two Pointers | Hard | The lower boundary determines guaranteed trapped water; update the side with the smaller max. | [Back-of-Envelope Estimation](../00-theory/system-design-fundamentals/back-of-envelope.md) | 30 min |
| 8 | [Maximum Sum Subarray of Size K](./sliding-window/02-maximum-sum-subarray-size-k.md) | Sliding Window | Easy | Reuse the previous window sum by subtracting the outgoing value and adding the incoming value. | [Realtime Metrics Platform](../04-hld-projects/realtime-metrics-platform/DESIGN.md) | 12 min |
| 9 | [Minimum Size Subarray Sum](./sliding-window/03-minimum-size-subarray-sum.md) | Sliding Window | Medium | Expand until feasible, then shrink while preserving the threshold condition. | [Rate Limiting](../03-hld-concepts/rate-limiting/THEORY.md) | 18 min |
| 10 | [Longest Substring Without Repeating Characters](./sliding-window/04-longest-substring-without-repeating.md) | Sliding Window | Medium | Keep a uniqueness invariant inside the window and advance the left boundary past conflicts. | [Idempotency](../03-hld-concepts/idempotency/THEORY.md) | 20 min |
| 11 | [Longest Substring With At Most K Distinct Characters](./sliding-window/05-longest-substring-at-most-k-distinct.md) | Sliding Window | Medium | Track active categories with counts; shrink only when the category budget is exceeded. | [Caching](../03-hld-concepts/caching/THEORY.md) | 22 min |
| 12 | [Subarrays With Exactly K Distinct Values](./sliding-window/06-subarrays-with-exactly-k-distinct.md) | Sliding Window | Hard | Convert exactly-K counting into at-most-K minus at-most-(K-1). | [Stream Processing](../03-hld-concepts/stream-processing/THEORY.md) | 30 min |
| 13 | [Permutation in String](./sliding-window/07-permutation-in-string.md) | Sliding Window | Medium | Compare fixed-size frequency signatures instead of generating permutations. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 22 min |
| 14 | [Sliding Window Maximum](./sliding-window/08-sliding-window-maximum.md) | Sliding Window | Hard | Maintain a monotonic deque so the current maximum is always at the front. | [Monitoring and Observability](../03-hld-concepts/monitoring-observability/THEORY.md) | 30 min |
| 15 | [Classic Binary Search](./binary-search/02-classic-binary-search.md) | Binary Search | Easy | Preserve an inclusive search interval and eliminate half only after comparing with the midpoint. | [Indexing](../00-theory/database-concepts/indexing.md) | 12 min |
| 16 | [First Position / Lower Bound](./binary-search/03-first-position-lower-bound.md) | Binary Search | Medium | Search for the first true boundary, not just any matching value. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 18 min |
| 17 | [Search in Rotated Sorted Array](./binary-search/05-search-in-rotated-sorted-array.md) | Binary Search | Medium | Identify which half remains sorted, then decide whether the target can live there. | [Consistent Hashing](../03-hld-concepts/consistent-hashing/THEORY.md) | 25 min |
| 18 | [Find Minimum in Rotated Sorted Array](./binary-search/06-find-minimum-in-rotated-sorted-array.md) | Binary Search | Medium | Compare midpoint to the right boundary to locate the rotation pivot. | [Database Sharding](../03-hld-concepts/database-sharding/THEORY.md) | 20 min |
| 19 | [Koko Eating Bananas](./binary-search/07-koko-eating-bananas.md) | Binary Search | Medium | Binary search the answer space only after proving the feasibility predicate is monotonic. | [Back-of-Envelope Estimation](../00-theory/system-design-fundamentals/back-of-envelope.md) | 28 min |
| 20 | [Search a 2D Matrix](./binary-search/08-search-a-2d-matrix.md) | Binary Search | Medium | Treat row-major matrix order as one sorted search space and map indexes carefully. | [Elasticsearch](../03-hld-concepts/elasticsearch/THEORY.md) | 22 min |

## Suggested Study Ladder

- **Foundation:** Rows 1, 2, 8, 15.
- **Interview-ready:** Rows 3, 4, 5, 9, 10, 11, 13, 16, 17, 18, 20.
- **Elite readiness:** Rows 6, 7, 12, 14, 19.

## Wave 3 Extension Ladder

After the top 20, use these rows to cover graph traversal, dynamic programming, greedy proof, backtracking, heap / priority queue, trie, and Union-Find fundamentals.

| Rank | Problem Source | Pattern | Difficulty | Core Insight | Related Repo Content | Time Target |
|---|---|---|---|---|---|---|
| 21 | [Binary Tree Level Order Traversal](./bfs-dfs/02-binary-tree-level-order-traversal.md) | BFS/DFS | Easy | Capture queue size at each layer so one BFS iteration maps to one tree level. | [Common Complexities](../00-theory/complexity-analysis/common-complexities.md) | 12 min |
| 22 | [Number of Islands](./bfs-dfs/03-number-of-islands.md) | BFS/DFS | Medium | Count connected components by starting flood fill only from unvisited land. | [Pattern to SD Map](./PATTERN-SD-MAP.md) | 18 min |
| 23 | [Course Schedule](./bfs-dfs/06-course-schedule.md) | BFS/DFS | Medium | Directed-cycle detection needs active-path state, not just a visited set. | [Workflow Orchestration](../03-hld-concepts/workflow-orchestration/THEORY.md) | 25 min |
| 24 | [Word Ladder](./bfs-dfs/07-word-ladder.md) | BFS/DFS | Hard | Treat words as an implicit unweighted graph and use BFS for shortest transformation length. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 30 min |
| 25 | [Climbing Stairs](./dynamic-programming/02-climbing-stairs.md) | Dynamic Programming | Easy | Define `dp[i]` as ways to reach step `i`; last move comes from `i-1` or `i-2`. | [Common Complexities](../00-theory/complexity-analysis/common-complexities.md) | 12 min |
| 26 | [House Robber](./dynamic-programming/03-house-robber.md) | Dynamic Programming | Medium | At each house choose skip or take current plus the best answer two positions back. | [Job Scheduler](../04-hld-projects/job-scheduler/) | 18 min |
| 27 | [Coin Change](./dynamic-programming/04-coin-change.md) | Dynamic Programming | Medium | Use an impossible-state sentinel and try every coin as the last coin. | [Token / Cost / Latency Planning](../06-genai-systems/00-concepts/token-cost-latency/README.md) | 25 min |
| 28 | [Longest Common Subsequence](./dynamic-programming/06-longest-common-subsequence.md) | Dynamic Programming | Medium | Prefix-pair DP separates match-diagonal and skip-one-side transitions. | [Two Pointers](./two-pointers/README.md) | 28 min |
| 29 | [Activity Selection](./greedy/02-activity-selection.md) | Greedy | Easy | Earliest finish is safe because it leaves at least as much room for future intervals. | [Job Scheduler](../04-hld-projects/job-scheduler/) | 15 min |
| 30 | [Jump Game](./greedy/04-jump-game.md) | Greedy | Medium | Farthest reachable boundary summarizes every useful prior jump. | [Load Balancing](../03-hld-concepts/load-balancing/THEORY.md) | 18 min |
| 31 | [Gas Station](./greedy/05-gas-station.md) | Greedy | Medium | A negative segment invalidates every start inside it, so the next start is after the failure. | [Quick Commerce Delivery](../04-hld-projects/quick-commerce-delivery/) | 22 min |
| 32 | [Minimum Arrows to Burst Balloons](./greedy/08-minimum-arrows-burst-balloons.md) | Greedy | Medium | Shooting at the earliest uncovered end covers the first interval while preserving future coverage. | [Caching](../03-hld-concepts/caching/THEORY.md) | 20 min |
| 33 | [Subsets](./backtracking/02-subsets.md) | Backtracking | Easy | Choose-or-skip recursion enumerates each subset exactly once. | [Pattern to SD Map](./PATTERN-SD-MAP.md) | 15 min |
| 34 | [Combination Sum](./backtracking/04-combination-sum.md) | Backtracking | Medium | Carry the start index and remaining target so pruning avoids duplicate combinations. | [Online Auction](../04-hld-projects/online-auction/) | 25 min |
| 35 | [Word Search](./backtracking/05-word-search.md) | Backtracking | Medium | Mark the current path, explore neighbors, then unmark to isolate branches. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 25 min |
| 36 | [N-Queens](./backtracking/07-n-queens.md) | Backtracking | Hard | Track occupied columns and diagonals so invalid branches stop before board scans. | [Movie Ticket Booking LLD](../02-lld-projects/movie-ticket-booking/) | 35 min |
| 37 | [Top K Frequent Elements](./heap-priority-queue/02-top-k-frequent-elements.md) | Heap / Priority Queue | Medium | Keep only K candidates in a bounded heap instead of sorting the whole frequency table. | [News Feed](../04-hld-projects/news-feed/) | 22 min |
| 38 | [Merge K Sorted Lists](./heap-priority-queue/04-merge-k-sorted-lists.md) | Heap / Priority Queue | Medium | A heap over current heads performs the next smallest global merge step. | [Message Queues](../03-hld-concepts/message-queues/THEORY.md) | 25 min |
| 39 | [Find Median from Data Stream](./heap-priority-queue/05-find-median-from-data-stream.md) | Heap / Priority Queue | Hard | Two heaps preserve lower and upper halves so the median is always at the boundary. | [Realtime Metrics Platform](../04-hld-projects/realtime-metrics-platform/) | 30 min |
| 40 | [Task Scheduler](./heap-priority-queue/06-task-scheduler.md) | Heap / Priority Queue | Medium | Priority plus cooldown state separates ready work from temporarily blocked work. | [Job Scheduler](../04-hld-projects/job-scheduler/) | 28 min |
| 41 | [Implement Trie / Prefix Tree](./trie/02-implement-trie-prefix-tree.md) | Trie | Medium | A path can exist without being a complete word; terminal markers define exact membership. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 20 min |
| 42 | [Word Dictionary Wildcard Search](./trie/03-word-dictionary-wildcard-search.md) | Trie | Medium | Fixed characters follow one child while `.` branches over children for exactly one position. | [Elasticsearch](../03-hld-concepts/elasticsearch/THEORY.md) | 25 min |
| 43 | [Map Sum Pairs](./trie/05-map-sum-pairs.md) | Trie | Medium | Prefix aggregates need delta updates when an existing key is overwritten. | [Realtime Metrics Platform](../04-hld-projects/realtime-metrics-platform/) | 25 min |
| 44 | [Word Search II](./trie/06-word-search-ii.md) | Trie + Backtracking | Hard | Trie prefix misses prune board DFS before impossible paths expand. | [Search Systems](../03-hld-concepts/search-systems/THEORY.md) | 35 min |
| 45 | [Number of Connected Components](./union-find/02-number-of-connected-components.md) | Union-Find | Medium | Each successful union between different roots removes exactly one component. | [LinkedIn Connection LLD](../02-lld-projects/linkedin-connection/) | 18 min |
| 46 | [Graph Valid Tree](./union-find/03-graph-valid-tree.md) | Union-Find | Medium | A valid undirected tree has `n - 1` edges and no same-root edge. | [Workflow Orchestration](../03-hld-concepts/workflow-orchestration/THEORY.md) | 20 min |
| 47 | [Accounts Merge](./union-find/05-accounts-merge.md) | Union-Find | Medium | Shared identifiers create components; output is grouped by final root and sorted. | [Bot Detection Platform](../04-hld-projects/bot-detection-platform/) | 30 min |
| 48 | [Satisfiability of Equality Equations](./union-find/08-satisfiability-of-equality-equations.md) | Union-Find | Medium | Equalities build equivalence classes first; inequalities reject same-root pairs. | [Distributed Coordination](../03-hld-concepts/distributed-coordination/THEORY.md) | 22 min |

## Review Checklist

- Can you state the invariant before writing code?
- Can you explain why the naive approach is too slow or too memory-heavy?
- Can you identify the exact boundary movement rule?
- Can you map the coding invariant to a production concern such as bounded memory, ordered lookup, ranking, compaction, or freshness?
- Can you name the failure mode if duplicates, skew, stale data, or late events appear?
