# Hld Projects Quiz - Answer Key

> **Detailed explanations for all 54 questions**

---

### Question 1
**Answer: D**

**Why Correct:**
- In a ride-sharing platform, ride assignment correctness is the critical consistency boundary because double-booking a driver or losing an assignment state causes direct operational failure and user dissatisfaction. While location updates are high-volume, they can tolerate eventual consistency. ETA and surge updates are also eventually consistent. Therefore, only ride assignment requires strong consistency.

**Why Not Distractors:**
- **A**: This distractor (Assuming that ride assignment ownership is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Surge multiplier refresh) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (ETA refresh stream) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-1)

### Question 2
**Answer: C**

**Why Correct:**
- A geospatial index, such as a Quadtree or Geohash-based inverted index, is designed specifically for efficient 2D spatial queries (e.g., finding nearby drivers within a radius). A full table scan would scale linearly with the number of drivers, causing unacceptable latency. Queues or linked lists are linear data structures unsuited for multi-dimensional spatial lookups.

**Why Not Distractors:**
- **A**: This distractor (Per-driver linked list) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Full table scan) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Queue by signup time) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-2)

### Question 3
**Answer: B**

**Why Correct:**
- In the standard ride lifecycle, a ride cannot jump directly from REQUESTED to COMPLETED without passing through intermediate states like MATCHED, DRIVER_EN_ROUTE, and IN_PROGRESS. Skipping these states violates the state machine's integrity. The other options represent valid transitions or logically impossible ones that aren't the primary anti-pattern here.

**Why Not Distractors:**
- **A**: This distractor (REQUESTED -> MATCHED) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (MATCHED -> DRIVER_EN_ROUTE) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (IN_PROGRESS -> COMPLETED) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-3)

### Question 4
**Answer: D**

**Why Correct:**
- Location telemetry generates extremely high write throughput (e.g., updates every 3 seconds per driver). If routed through the same system as ride lifecycle commands (which require transactional correctness), telemetry spikes could exhaust database connections and lock up the critical path. Separating them ensures command path stability.

**Why Not Distractors:**
- **A**: This distractor (To simplify API docs) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (To avoid using message queues) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that to isolate write-heavy telemetry from correctness-critical transitions is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-4)

### Question 5
**Answer: B**

**Why Correct:**
- When a driver fails to respond to an offer, the system should automatically timeout the offer and move to the next highest-ranked candidate to minimize user wait time. Waiting indefinitely stalls the ride, cancelling immediately degrades user experience, and retrying the same unresponsive driver wastes precious time.

**Why Not Distractors:**
- **A**: This distractor (Wait forever for accept) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Move to next ranked candidate without timeout policy) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Retry same driver indefinitely) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-5)

### Question 6
**Answer: B**

**Why Correct:**
- Mobile networks are unreliable, meaning users might unknowingly double-tap or auto-retry ride requests. An idempotency key ensures that the backend recognizes duplicate requests and returns the existing ride state rather than creating multiple rides and charging the user twice.

**Why Not Distractors:**
- **A**: This distractor (Compress payload size) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Encrypt ride data) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that prevent duplicate ride creation during retries is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-6)

### Question 7
**Answer: A**

**Why Correct:**
- If the matching system is degrading, it will struggle to find drivers, leading to deeper retry chains (offer retry depth) and longer times to secure a match (match tail latency). Driver profile photo size or app install count are unrelated to realtime backend matching health.

**Why Not Distractors:**
- **B**: This distractor (Assuming that offer retry depth and match tail latency is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Average trip distance) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (App install count) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-7)

### Question 8
**Answer: B**

**Why Correct:**
- Ride-sharing operations are naturally constrained by geography; a driver in New York cannot pick up a rider in Tokyo. Partitioning operational state by city allows the system to scale horizontally and isolates regional outages, while shared identity/billing handles user roaming.

**Why Not Distractors:**
- **A**: This distractor (Global shared queue for all cities only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (One cache key for all cities) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (City-scoped operational partitions without shared identity/billing) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-8)

### Question 9
**Answer: C**

**Why Correct:**
- Driver locations change constantly, and the exact real-time position is less critical than an approximate recent location for the matching funnel. Therefore, eventual consistency with bounded staleness is acceptable, whereas strong consistency would impose crippling latency on the write path.

**Why Not Distractors:**
- **A**: This distractor (Eventual consistency is acceptable without bounded staleness) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Locations should never be cached) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (No consistency model is needed) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-9)

### Question 10
**Answer: A**

**Why Correct:**
- An exchange adapter is responsible for abstracting the specific protocols (like FIX or proprietary binary APIs) of external exchanges, converting internal normalized orders into exchange-specific formats, routing them, and tracking their lifecycle against the external venue.

**Why Not Distractors:**
- **B**: This distractor (Match market participants internally) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Ignore external execution state) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Never route orders and track lifecycle against exchanges during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-10)

### Question 11
**Answer: A**

**Why Correct:**
- Submitting or cancelling an order modifies financial state. If a network timeout occurs, the client must be able to safely retry the command without risking a duplicate execution. Thus, submit/cancel operations must be strictly idempotent to prevent unintended financial exposure.

**Why Not Distractors:**
- **B**: This distractor (GET quote) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Heartbeat ping) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Static metadata read) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-11)

### Question 12
**Answer: A**

**Why Correct:**
- Quote fanout involves extreme high-throughput, low-latency broadcast (reads), while order commands involve high-stakes, transactional state mutations (writes). Splitting them prevents read-heavy market data bursts from starving the connection pools or CPU required for critical order execution.

**Why Not Distractors:**
- **B**: This distractor (To isolate high-latency fanout from correctness-critical workflows) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (To remove all storage layers) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (To use different programming languages) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-12)

### Question 13
**Answer: D**

**Why Correct:**
- When interacting with external venues, network disconnects can leave an order in an ambiguous state (e.g., submitted but ack/timeout missed). A reconciliation worker asynchronously verifies the external venue's state against the internal database to resolve these hanging orders.

**Why Not Distractors:**
- **A**: This distractor (DNS cache warmup) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Keyboard shortcut conflict) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that ambiguous external exchange ack/timeout is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-13)

### Question 14
**Answer: B**

**Why Correct:**
- Financial systems require absolute correctness for state transitions. The final order state must be strongly consistent locally (typically via ACID database transactions) and accompanied by a durable event trail (audit log) to ensure regulatory compliance and exact recovery.

**Why Not Distractors:**
- **A**: This distractor (Cache-only state) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (No persistence needed) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Strong local state transitions without durable event trail) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-14)

### Question 15
**Answer: B**

**Why Correct:**
- Websockets provide persistent, full-duplex connections. This pushes quote updates to the client instantly as they happen, yielding much lower fanout latency compared to polling, and significantly reducing backend CPU and network overhead by eliminating repeated HTTP request headers.

**Why Not Distractors:**
- **A**: This distractor (Assuming that lower fanout latency and lower polling overhead is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Higher storage durability) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Eliminates backpressure risks entirely) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-15)

### Question 16
**Answer: C**

**Why Correct:**
- The primary purpose of an exchange adapter is timely order execution. Ack timeout rate measures how often the venue fails to respond in time, and reconciliation lag measures how far behind the background state sync is. High values in these metrics indicate adapter or venue distress.

**Why Not Distractors:**
- **A**: This distractor (Assuming that ack timeout rate and reconciliation lag is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Logo load time) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Team meeting count) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-16)

### Question 17
**Answer: A**

**Why Correct:**
- The lifecycle of an order determines financial exposure. Therefore, the source of truth must be a highly durable, highly available database (often paired with an event log) rather than volatile caches or client-side storage, ensuring no state is lost during node crashes.

**Why Not Distractors:**
- **B**: This distractor (Assuming that durable order DB + event log is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Browser localStorage) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (In-memory object only) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-17)

### Question 18
**Answer: D**

**Why Correct:**
- In a financial system, if an upstream execution venue is down, the adapter must immediately stop accepting new orders for that venue via a circuit breaker. This prevents order backlog accumulation and clearly surfaces the degraded status to downstream components or users.

**Why Not Distractors:**
- **A**: This distractor (Disable quote updates permanently) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Accept all orders as filled) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that circuit-break adapter and surface explicit degraded status is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-18)

### Question 19
**Answer: A**

**Why Correct:**
- In real-time collaborative editing (like OT or CRDT), multiple users can edit simultaneously. The primary correctness goal is that, despite concurrent and potentially conflicting operations arriving out of order, all clients eventually converge to the exact same document state.

**Why Not Distractors:**
- **B**: This distractor (Never allowing concurrent writes) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Single-editor lock per document forever) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Strong serializability for every keystroke globally) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-19)

### Question 20
**Answer: D**

**Why Correct:**
- To properly apply a concurrent edit, the system must know which document state the client was looking at when the edit was made. Tracking the `base_version` (or operation ID) allows the server to safely validate, transform (rebase), and apply the operation against the current server state.

**Why Not Distractors:**
- **A**: This distractor (To reduce websocket count) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (To increase font rendering quality) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that to validate/rebase concurrent operations safely is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-20)

### Question 21
**Answer: C**

**Why Correct:**
- Mobile networks frequently drop connections. When a client reconnects, replay-on-reconnect allows the client to fetch all operations that occurred on the document while they were offline, seamlessly merging them with their local pending edits without needing a full document reload.

**Why Not Distractors:**
- **A**: This distractor (Recovering missed operations before disconnect) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Removing old snapshots) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Auto-formatting markdown) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-21)

### Question 22
**Answer: C**

**Why Correct:**
- Applying an entire operation log from version zero to a million is too slow. Periodic snapshots store the complete document state at specific intervals. To recover, a client only needs to load the most recent snapshot and replay the small tail of operations that occurred since.

**Why Not Distractors:**
- **A**: This distractor (To avoid all storage writes) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that to bound replay cost and recovery time is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (To increase network latency) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-22)

### Question 23
**Answer: C**

**Why Correct:**
- Collaboration requires sequentializing concurrent edits. Routing all users editing the same document to the same server (document-affinity session routing) allows that server to serialize operations efficiently in-memory, avoiding complex distributed locking across the fleet.

**Why Not Distractors:**
- **A**: This distractor (Assuming that document-affinity session routing is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (One global lock server only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Polling every 30 seconds) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-23)

### Question 24
**Answer: D**

**Why Correct:**
- Assuming that the order in which a websocket server receives messages equals the correct global consistency order is a major anti-pattern. Network latency varies, so operations must be explicitly ordered and transformed (via OT/CRDT) based on their logical versions, not just arrival time.

**Why Not Distractors:**
- **A**: This distractor (Separating metadata CRUD from realtime path) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that assuming websocket order equals global consistency is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Explicit operation schema) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-24)

### Question 25
**Answer: A**

**Why Correct:**
- If OT/CRDT transformations fail repeatedly due to severe divergence or bugs, the safest fallback is to force the client to resync completely. It discards corrupted local state, fetches the latest server snapshot plus recent operations, and re-establishes a clean baseline.

**Why Not Distractors:**
- **B**: This distractor (Disable all edits) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Mark document deleted) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Never force client resync from latest snapshot + replay window during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-25)

### Question 26
**Answer: C**

**Why Correct:**
- Session-path stress in a real-time system is directly tied to operation throughput and connection stability. Replay latency (how long it takes to catch up) and reconnect recovery failures directly indicate that the server is struggling to process the event loop or handle state synchronization.

**Why Not Distractors:**
- **A**: This distractor (Never replay latency and reconnect recovery failures during normal operations) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Number of emojis in doc) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Desktop wallpaper color) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-26)

### Question 27
**Answer: A**

**Why Correct:**
- Core document content (operation logs and snapshots) must be strictly durable to prevent data loss. However, ephemeral data like real-time cursor positions or presence indicators do not require database persistence, as they lose relevance instantly if the session drops.

**Why Not Distractors:**
- **B**: This distractor (Assuming that operation log/snapshots durable; transient presence can be ephemeral is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Presence cursor positions are always strongly durable) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (No persistence needed) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-27)

### Question 28
**Answer: A**

**Why Correct:**
- When scaling a distributed cache, adding or removing nodes typically forces a massive rehashing of keys. Consistent hashing minimizes this disruption by mapping keys to a ring, ensuring that only a small fraction of keys are remapped when the cluster topology changes.

**Why Not Distractors:**
- **B**: This distractor (Perfect hot-key elimination) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that reduced key remapping when node membership changes is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Strong transactions by default) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-28)

### Question 29
**Answer: B**

**Why Correct:**
- Caches are generally used to offload read traffic and tolerate some staleness. Therefore, eventual consistency is typical, prioritizing high availability and low latency. Strict serializability would impose coordination overhead that defeats the purpose of the cache.

**Why Not Distractors:**
- **A**: This distractor (No replication) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Write-once immutability only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Eventual consistency without availability priority) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-29)

### Question 30
**Answer: A**

**Why Correct:**
- Time-to-Live (TTL) dictates how long a key remains in the cache before it is automatically evicted. This limits how stale the cached data can become relative to the source of truth and prevents the cache from growing indefinitely with rarely accessed keys.

**Why Not Distractors:**
- **B**: This distractor (Network encryption) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that data freshness and automatic expiry is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Consistent hashing ring size) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-30)

### Question 31
**Answer: C**

**Why Correct:**
- When a single key becomes extremely hot (e.g., a viral video metadata request), all consistent hashing traffic concentrates on one node, causing a localized meltdown. Local fallback caching (in-memory on the application nodes) or adaptive replication spreads this hot read load.

**Why Not Distractors:**
- **A**: This distractor (Turn off cache) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that adaptive replication and local fallback caching is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Delete key always) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-31)

### Question 32
**Answer: C**

**Why Correct:**
- Modulo routing (`hash(key) % N`) uses the total node count `N`. If `N` changes (e.g., a node crashes), the modulo for almost all keys changes, resulting in massive cache misses and a "thundering herd" of traffic to the backing database, potentially causing cascading failure.

**Why Not Distractors:**
- **A**: This distractor (It prevents replication) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that it remaps most keys on node count changes is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (It is too secure) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-32)

### Question 33
**Answer: A**

**Why Correct:**
- When rebalancing a cluster, instantly moving all keys causes massive network saturation, and stopping traffic causes downtime. Progressive range movement with guardrails allows the system to slowly migrate key ownership while continuing to serve reads and writes safely.

**Why Not Distractors:**
- **B**: This distractor (Move all keys instantly) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Progressive range movement without guardrails) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Recreate entire cluster daily) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-33)

### Question 34
**Answer: D**

**Why Correct:**
- If a cache goes down, failing open (routing all traffic to the database) without limits can instantly crush the database. The system must fallback to the source but strictly enforce backpressure controls (rate limits or circuit breakers) to protect the source of truth.

**Why Not Distractors:**
- **A**: This distractor (Fallback to source without backpressure controls) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Blindly fail all requests) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Return random values) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-34)

### Question 35
**Answer: C**

**Why Correct:**
- A cache's value is determined by its ability to offload the database and serve requests quickly. Hit ratio measures offload efficiency, while miss penalty latency measures the cost of fetching from the database. Together, they accurately capture cache performance stress.

**Why Not Distractors:**
- **A**: This distractor (Assuming that hit ratio + miss penalty latency is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Dark mode usage + app icon size) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Commit message length) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-35)

### Question 36
**Answer: C**

**Why Correct:**
- A cache is an optimization layer, not a durable system of record. Because it is volatile and relies on eviction/TTL, treating a cache as the source of truth is inherently unsafe. The backing durable store (e.g., a relational database) must always own data correctness.

**Why Not Distractors:**
- **A**: This distractor (Assuming that unsafe by default; backing store owns correctness is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Always safe for financial correctness) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Eliminates need for database) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-36)

### Question 37
**Answer: B**

**Why Correct:**
- Large video files take significant time to upload. If a network drop interrupts a 5GB upload at 99%, restarting from zero is unacceptable. Multipart resumable upload sessions allow the client to retry only the failed chunks, safely recovering from interruptions.

**Why Not Distractors:**
- **A**: This distractor (Assuming that to recover from large-file upload interruptions safely is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (To avoid object storage) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (To remove metadata needs) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-37)

### Question 38
**Answer: C**

**Why Correct:**
- Video transcoding is intensely CPU-heavy and slow. Performing it inline during an HTTP request would cause timeouts and tie up web server threads. Transcoding must be pushed to an async processing queue where a dedicated worker fleet can scale independently to handle the load.

**Why Not Distractors:**
- **A**: This distractor (Browser-side transcoding only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that async processing queue and worker fleet is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Inline transcode in upload HTTP request) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-38)

### Question 39
**Answer: A**

**Why Correct:**
- To support Adaptive Bitrate Streaming (ABR), the player needs to know which resolutions and bitrates are available. The playback manifest (e.g., HLS .m3u8 or DASH .mpd) provides this metadata, allowing the client to request the optimal video segments based on current bandwidth.

**Why Not Distractors:**
- **B**: This distractor (Employee payroll data) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that variant/segment metadata for adaptive playback is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Distributed lock ownership) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-39)

### Question 40
**Answer: D**

**Why Correct:**
- Video segments are large, static assets requested millions of times. Serving them from a central database or origin server would cause immediate bottlenecking. A CDN caches these segments at the network edge, absorbing massive read traffic and minimizing startup latency for users.

**Why Not Distractors:**
- **A**: This distractor (It removes need for manifests) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (It replaces object storage durability) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (It absorbs low read traffic and lowers startup latency in most system architectures) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-40)

### Question 41
**Answer: B**

**Why Correct:**
- A manifest should only be served to users when the video is actually playable. This requires the state to transition from PROCESSING (transcoding) to READY only after the variant generation succeeds and the segments are durably stored on the origin or CDN.

**Why Not Distractors:**
- **A**: This distractor (PROCESSING -> READY before variant generation succeeds) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (INITIATED -> FAILED only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (READY -> INITIATED) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-41)

### Question 42
**Answer: A**

**Why Correct:**
- If one resolution variant (e.g., 4K) fails to transcode but the 1080p variant succeeds, the video is still playable. The best practice is to serve the available lower-quality variants to unblock the user while asynchronously retrying the failed job in the background.

**Why Not Distractors:**
- **B**: This distractor (Mark every upload as failed) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that serve available lower-quality variant while retrying failed jobs is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Disable CDN) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-42)

### Question 43
**Answer: D**

**Why Correct:**
- Video streaming quality is primarily judged by how fast the video starts (startup latency) and how often it pauses to buffer (rebuffer ratio). High rebuffering directly indicates CDN cache misses, inadequate bandwidth, or poor adaptive bitrate algorithm performance.

**Why Not Distractors:**
- **A**: This distractor (Upload title length) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Assuming that startup latency and rebuffer ratio is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Avatar resolution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-43)

### Question 44
**Answer: D**

**Why Correct:**
- When a video goes viral, read traffic spikes exponentially. Proactive cache warming pre-loads the video segments into the CDN, and origin shielding collapses multiple CDN edge misses into a single origin request, protecting the storage layer from a thundering herd.

**Why Not Distractors:**
- **A**: This distractor (Proactive database warming + origin shielding) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Turn off uploads globally) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Remove manifests) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-44)

### Question 45
**Answer: A**

**Why Correct:**
- Keeping all video assets in hot storage is cost-prohibitive. Most videos follow a zipfian access pattern where viewership drops sharply after a few days. Implementing lifecycle tiering automatically moves older, rarely accessed blobs to cheaper cold storage tiers, optimizing costs.

**Why Not Distractors:**
- **B**: This distractor (Keep all assets in one hot tier forever) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Delete old videos aggressively regardless policy) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Store blobs only in relational rows) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-45)

### Question 46
**Answer: D**

**Why Correct:**
- Content moderation involves irreversible actions like account deletion. Confidence-aware routing ensures that only items flagged with exceptionally high ML confidence are auto-removed. Borderline cases are routed to human reviewers, providing a crucial precision guardrail.

**Why Not Distractors:**
- **A**: This distractor (Assuming that to separate auto-remove from review pathways under precision guardrails is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (To avoid storing audit logs) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (To bypass human reviewers completely) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-46)

### Question 47
**Answer: B**

**Why Correct:**
- Machine learning models drift over time as bad actors evolve tactics. Reviewer disagreement rate (when humans override ML decisions) and precision@action degradation clearly indicate that the model is losing accuracy and needs retraining on fresh data.

**Why Not Distractors:**
- **A**: This distractor (Cloud region count) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Number of API endpoints) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that reviewer disagreement rate and precision@action degradation is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-47)

### Question 48
**Answer: B**

**Why Correct:**
- Deploying a new moderation policy is risky; an overly aggressive rule could auto-suspend thousands of innocent users. A canary rollout with rollback gates on guardrail metrics limits the blast radius, allowing engineers to verify precision before applying the policy globally.

**Why Not Distractors:**
- **A**: This distractor (Remove all review queues) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Global threshold change in one shot) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Canary rollout without rollback gates on guardrail metrics) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-48)

### Question 49
**Answer: B**

**Why Correct:**
- Supervised models are highly accurate at catching known, historical bot campaigns, but they fail against novel tactics. Anomaly detection identifies unusual behavior spikes regardless of history. Blending both ensures defense against both recognized threats and zero-day attacks.

**Why Not Distractors:**
- **A**: This distractor (To increase UI animation quality) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (To remove need for telemetry) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that to catch known campaigns and novel attacks together is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-49)

### Question 50
**Answer: C**

**Why Correct:**
- When a bot score is uncertain, immediate permanent suspension risks severe false positives. A confidence-aware ladder applies graduated friction—such as rate limiting or issuing CAPTCHA challenges—allowing legitimate users to prove their humanity while halting bots.

**Why Not Distractors:**
- **A**: This distractor (Confidence-aware ladder: allow/limit/challenge/suspend without escalation) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Ignore score and trust user reports only) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Immediate permanent suspension always) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-50)

### Question 51
**Answer: B**

**Why Correct:**
- Coordinated bot campaigns often test defenses, finding ways to slip past models. A sudden spike in the campaign-level bypass rate (bots succeeding) and a surge in the investigator queue (humans overwhelmed by borderline cases) are clear operational indicators of a targeted attack.

**Why Not Distractors:**
- **A**: This distractor (Login page font size) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that campaign-level bypass rate and investigator queue surge is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Avatar upload count) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-51)

### Question 52
**Answer: B**

**Why Correct:**
- Evaluating a deep neural network on billions of videos is computationally impossible within latency budgets. Separating generation (cheaply retrieving thousands of candidates) from ranking (applying heavy ML models to the top 100) satisfies latency constraints while preserving quality.

**Why Not Distractors:**
- **A**: This distractor (To avoid feature stores entirely) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (To ensure only one model is ever used) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **D**: This distractor (Assuming that to satisfy latency budgets while still using richer features in later stages is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-52)

### Question 53
**Answer: D**

**Why Correct:**
- Pure exploitation creates filter bubbles, while pure exploration degrades immediate user experience. Applying bounded explore traffic ensures new content is discovered, while guardrails on watch-time and safety metrics ensure the exploration doesn't destabilize overall platform quality.

**Why Not Distractors:**
- **A**: This distractor (Apply bounded explore traffic without guardrails on watch-time and safety metrics) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Disable exploration permanently) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Always rank by creator upload time only) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-53)

### Question 54
**Answer: D**

**Why Correct:**
- When a dominant creator cohort monopolizes engagement labels, standard ML models will continuously rank them higher, creating an unfair loop. Adding cohort-aware constraints and monitoring exposure parity forces the ranker to allocate fair visibility to minority cohorts without abandoning relevance.

**Why Not Distractors:**
- **A**: This distractor (Force strict round-robin ranking for all users) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **B**: This distractor (Remove personalization and use one global ranking list) represents a suboptimal trade-off or incorrect assumption for this scenario.
- **C**: This distractor (Assuming that add cohort-aware constraints and monitor exposure parity alongside relevance metrics is the only solution) represents a suboptimal trade-off or incorrect assumption for this scenario.

[Read more about this architecture pattern](../hld-projects-quiz.md#question-54)
