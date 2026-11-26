# Distributed Social Graph Engine - Follow-Up Questions

## Follow-up questions

**1. How do you handle pagination through a massive association list (e.g., millions of followers)?**
- *Expected Answer:* The cache only holds the $N$ most recent edges. When a user paginates past $N$, it's a guaranteed cache miss. The request is routed to the Leader, which queries the DB using an index on `(id1, atype, time DESC)`. To avoid heavy DB load for deep pagination of supernodes, cursor-based pagination (using the `time` or a unique edge ID) is required rather than `OFFSET/LIMIT`.

**2. What happens if the asynchronous invalidation bus (Wormhole) goes down or severely lags?**
- *Expected Answer:* Stale data will be served by Follower caches in replica regions. To mitigate:
  - We can attach a version number or timestamp to objects.
  - If a user performs a write, we store the resulting version in their local browser/app session.
  - On subsequent reads, the client sends this expected version. If the local Follower cache has an older version (due to lag), it forcefully bypasses its cache and queries the Leader (or DB) to fetch the latest data, ensuring "read-your-writes" even during replication lag.

**3. How do you handle a DB Master failure in the primary region?**
- *Expected Answer:* A replica in the primary region (or a replica in a secondary region if the whole region fails) must be promoted to Master. During the promotion window (which may take seconds to minutes), writes will fail. However, because we have a heavily cached read architecture (Followers), read availability remains near 100%, serving slightly stale data until the new Master is online.

## Variants and extensions

**1. "Inverse" Queries:**
- *Scenario:* We optimized for `id1 -> id2` (e.g., "Who does User A follow?"). How do we efficiently query "Who follows User B?" if we only sharded by `id1`?
- *Approach:* When User A follows User B, we must write *two* directed edges: `(A, FOLLOWS, B)` sharded by A, and `(B, FOLLOWED_BY, A)` sharded by B. This duplicates data but allows $O(1)$ lookups for both query directions.

**2. Access Control / Privacy:**
- *Scenario:* How do you ensure User A cannot see Post B if User C (the author) made it private?
- *Approach:* Access control checks are usually too complex to bake directly into the graph storage tier. The Graph Engine returns the raw edges (e.g., User A's feed). The web tier or a dedicated privacy service then filters the results based on ACL rules before returning them to the client. Alternatively, simple privacy rules (like 'visible_to_friends_only') can be stored as metadata on the Object itself, allowing the Follower cache to do lightweight filtering.

## Interviewer probes to prepare

- **Probe:** "You mentioned caching the most recent edges. What if the user deletes a very old edge that isn't in the cache? Does the cache need to know?"
  - *Response:* The cache primarily serves point lookups and recent list fetches. If an old edge is deleted, the invalidation bus still broadcasts the delete. The Follower cache checks if it holds that specific edge; if not, it does nothing. The persistent DB handles the actual deletion.
- **Probe:** "Why not just use Cassandra? It handles writes well and is distributed."
  - *Response:* Cassandra is excellent for writes, but its read latency for range queries (like time-ordered edge lists) across different partitions can be unpredictable. The TAO architecture heavily favors extreme read performance (P99 < 5ms) via an intelligent, graph-aware caching layer on top of a mature storage engine (MySQL), rather than relying purely on the DB's internal caching.

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [DESIGN.md](./DESIGN.md)