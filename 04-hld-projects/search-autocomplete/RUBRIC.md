# Search Autocomplete - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | What strong answers show |
|---|---|---|
| Requirements & Estimation | 15% | Identifies core constraints (latency) and correctly calculates peak QPS (48k) and storage needs (27 GB RAM for Trie). |
| Data Structures | 25% | Deeply understands Trie, O(p + m log k) traversal cost, and optimizes lookup to O(p) via node-level top-K caching. |
| Read/Write Path Separation | 25% | Explicitly decouples fast read path (Cache/Trie lookups) from slow write path (Analytics logging/Batch jobs). |
| Scale & Performance | 20% | Mentions CDN edge caching, browser caching, sampling rates for analytics, and Trie sharding strategies for >27GB. |
| Resilience & Trade-offs | 15% | Addresses cache stampede, stale data tolerance (availability > consistency), and real-time vs batch trade-offs. |

## Performance bands
- **Strong Hire:** Clear architecture separating read/write. Explains Trie optimization (caching top-5 at nodes). Handles scale well with sharding and edge caching.
- **Hire:** Solid architecture. Understands Trie structure. Might miss some optimizations like sampling analytics or edge caching.
- **No Hire:** Focuses heavily on synchronous real-time Trie updates. Fails to optimize read path latency. Cannot explain Trie complexities.

## Cross-links
- [Problem](PROBLEM.md)
- [Design](DESIGN.md)
