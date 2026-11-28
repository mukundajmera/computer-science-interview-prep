# Discord Message Storage Case Study

How a very large chat service evolved its message store from a single-database deployment to a purpose-shaped, partitioned system holding trillions of messages, and why it eventually replaced its database engine rather than its data model.

## 1. Problem Statement

### Business Challenge

Discord is a persistent group-chat product: servers (guilds) contain channels, and every message ever sent to a channel is expected to remain readable indefinitely. Unlike ephemeral chat or activity feeds, chat history is the product. Users scroll back years, search across channels, and expect the newest messages to appear in near real time. That combination, unbounded retention plus interactive read latency plus relentless write volume, is what makes message storage the hard core of the system.

### Technical Requirements

- Append-heavy writes: messages are written once, rarely edited, sometimes deleted.
- Read pattern: recent-history reads dominate (the last screen of messages per open channel), with a long tail of scroll-back and search.
- Per-channel ordering: messages within a channel must have a stable, time-consistent order.
- Unbounded growth: storage grows monotonically; nothing is expired by product policy.
- Low tail latency: a slow p99 on message reads is immediately user-visible as laggy channel loads.
- Availability over strict consistency for reads: a momentarily missing or reordered edge message is tolerable; a channel that will not load is not.

### Scale Metrics

- **Messages stored**: "billions" as publicly described in 2017 (Discord engineering blog), growing to "trillions" as publicly described in 2023 (Discord engineering blog). These are the company's own published figures.
- **Write volume**: not publicly stated as a precise rate; describe qualitatively as hundreds of millions to billions of messages per day at the 2023 scale. *Labelled estimate*: at 1 billion messages/day and ~100 bytes of message payload, raw payload alone is ~100 GB/day, ~36 TB/year before replication and metadata; index, replica, and compaction overhead multiply that several-fold.
- **Channel count and distribution**: extremely skewed. Most channels are small and quiet; a small number of very large public-server channels carry disproportionate traffic. This skew, not the average, is what shapes the design.
- **Cluster size**: node counts have been discussed publicly at points in time but change constantly; treat any specific number as dated and describe the shape instead (dozens to low hundreds of database nodes).

## 2. Architecture Evolution

### Phase 1: Launch on a General-Purpose Document Store

As publicly described in Discord's 2017 engineering post, the earliest versions of Discord stored messages in MongoDB. That was the right call for a product finding its shape: flexible schema, fast iteration, and operations a tiny team could run. The limitation appeared with growth: message volume is the one workload that never stops growing, and a single replica-set design offered no clean horizontal partitioning story for an unbounded, append-only dataset.

The launch-era lesson generalizes: pick the store that lets you ship, but keep the write path simple enough that a future migration only has to move data, not untangle features.

### Phase 2: Cassandra with Channel-and-Time Partitioning (2017 era)

The first at-scale design, described in the 2017 post "How Discord Stores Billions of Messages", moved messages to Cassandra and introduced the data model the company would keep for years:

- **Message IDs are time-ordered.** Discord uses Snowflake-style IDs (the approach popularized by Twitter): each ID embeds a timestamp, so IDs sort roughly by creation time without a separate sort key.
- **Partition key = (channel, time bucket).** Messages are partitioned by channel ID, and each channel's history is chopped into fixed time buckets (on the order of days per bucket, derived from the message ID's timestamp). A bucket is the unit of storage: reading recent history means reading the current bucket, and old buckets become immutable and cold.

This design answered the unbounded-growth problem: no partition grows forever, because a busy channel simply rolls into a fresh bucket. It also made the dominant read, "the last screen of messages", a single-partition, sequential read. Immutability of old buckets is an operational gift: they compact once, back up once, and sit in cache-friendly stillness.

The cost model worth stating in an interview: the same channel key that makes reads local also concentrates writes. Every message to a hot channel lands on the small set of nodes owning its current bucket.

### The 2017 Data Model, Made Concrete

An illustrative layout (not real IDs):

```text
channel 1234, bucket A (earlier window)     channel 1234, bucket B (current window)
  msg 8810..  10:00:01  "hello"               msg 8841..  09:15:22  "morning"
  msg 8811..  10:00:04  "world"               msg 8842..  09:15:40  "hi all"
channel 9876, bucket A (earlier window)
  msg 8825..  11:41:00  "gg"
```

- Reading a channel's latest screen = read bucket B of channel 1234, newest first: one partition, sequential.
- Scroll-back past the window = read bucket A next; no other channel's data is ever touched.
- A busy channel rolls from bucket B to bucket C when the window closes; bucket B becomes immutable history.

### Phase 3: ScyllaDB plus a Rust Data-Services Layer (2023 era)

The 2023 post "How Discord Stores Trillions of Messages" describes the second migration. The data model survived essentially unchanged; the engine and the access layer did not:

- **Cassandra was replaced by ScyllaDB**, a Cassandra-compatible reimplementation in C++ with a shard-per-core architecture, keeping the same query model and drivers while leaving the JVM behind.
- **A "data services" layer in Rust** was placed between the API monolith and the database. All message queries route through it, and it performs *request coalescing*: when many concurrent requests ask for the same data (a busy channel's first screen), only one database query is issued and the result is fanned out to all waiters.

The migration itself followed the standard live-migration shape for systems that cannot stop: run old and new in parallel, backfill history, verify reads against both, then cut traffic over gradually with the ability to fall back. The interview-relevant point is that this is survivable at trillion-message scale only because the data model and the client contract did not change.

### The Write Path, End to End

1. A client sends a message; the API tier assigns a Snowflake-style ID, which fixes the message's timestamp, order, and bucket in one value.
2. The write routes to the database nodes owning the `(channel_id, current_bucket)` partition.
3. Replicas acknowledge per the configured consistency level; the message is immediately part of the channel's newest bucket.
4. When the bucket window rolls, the next write opens a fresh partition; the old bucket never receives another write.

### The Read Path, End to End

1. A client opens a channel, asking for the most recent messages before ID `X` (or the latest, on first open).
2. The request enters the Rust data-services tier, which checks whether an identical query is already in flight.
3. If yes, the request attaches to the in-flight query (coalescing); if no, a new query goes to the database for the relevant bucket(s).
4. Scroll-back crosses bucket boundaries transparently: older buckets are read in turn, and their immutability makes them ideal cache candidates.

Neither path ever performs a cross-channel scatter-gather, which is the entire point of the partition design.

## 3. Key Design Decisions (and Rejected Alternatives)

### Decision 1: Partition by channel and time bucket

**Chosen**: `(channel_id, bucket)` as the partition key, with buckets derived from the time-ordered message ID.

**Why**: per-channel reads are the dominant access pattern, time buckets bound partition size forever, and immutable old buckets are cheap to compact, back up, and cache.

**Rejected alternatives**:

- *Partition by channel alone*: a mega-channel's partition grows without bound, recreating the classic big-partition failure that the design exists to avoid.
- *Partition by user*: chat reads are channel-centric, not user-centric; user partitioning would turn every channel read into a scatter-gather.

### Decision 2: Time-ordered (Snowflake) message IDs

**Chosen**: IDs that embed a timestamp, making IDs self-sorting and self-bucketing.

**Why**: ordering, pagination ("messages before this ID"), and bucket assignment all fall out of the ID itself; no separate sequence or timestamp index is needed.

**Rejected alternative**: *random UUIDs plus a created-at column*, which needs a secondary index for ordering and breaks the cheap "give me what changed since ID X" read.

### Decision 3: Replace the engine, not the model (Cassandra to ScyllaDB)

**Chosen**: keep the proven data model and CQL interface, swap the engine to ScyllaDB.

**Why**: the pain was operational, not logical (covered in Failure Modes). ScyllaDB's shard-per-core C++ design removes JVM garbage collection from the equation and gives far more consistent tail latency, while Cassandra wire-compatibility keeps the migration incremental.

**Rejected alternatives**:

- *Keep tuning Cassandra*: the company had already spent years tuning; the fundamental JVM and operational costs remained.
- *Migrate to a different data model or database family*: a rewrite of both model and engine at trillion-message scale is a multi-year risk with no clear payoff, since the model itself was not the bottleneck.

### Decision 4: Request coalescing in a dedicated data-services tier

**Chosen**: a Rust service layer that deduplicates identical in-flight queries before they hit the database.

**Why**: chat reads are heavily correlated. When a popular channel loads, thousands of clients ask for the same recent messages within the same second; coalescing turns that thundering herd into one database query. Routing traffic through a service tier also created one place to enforce caching, retries, and future schema evolution.

**Rejected alternative**: *let each API worker query the database directly*, which multiplies identical reads by concurrency and couples database behavior to every API deploy.

### Decision 5: A custom access tier instead of an off-the-shelf proxy

**Chosen**: build the data-services layer in Rust rather than adopting a generic database proxy or embedding logic in the API monolith.

**Why**: coalescing is chat-specific (the dedup key is the logical query, not a cache entry), and the tier had to be cheap enough to sit in front of every message read. A systems language with predictable latency fits that; the API monolith did not.

**Rejected alternative**: *generic proxy or cache tier*, which would deduplicate responses but not understand query semantics, pagination cursors, or bucket boundaries well enough to coalesce safely.

## 4. Technologies Used

| Layer | Choice | Role | Alternative considered |
|---|---|---|---|
| Message IDs | Snowflake-style time-ordered IDs | Ordering, pagination, bucketing | UUID + timestamp index |
| Message store (2017) | Cassandra | Partitioned, replicated message storage | MongoDB sharding (outgrown) |
| Message store (2023) | ScyllaDB | Same model, no JVM, shard-per-core | Tuned Cassandra; non-CQL stores |
| Data access tier | Rust "data services" | Coalescing, caching, routing | Direct queries from the API tier |
| Bucket scheme | Fixed time windows per channel | Bounded partitions, immutable history | Unbounded per-channel partitions |

## 5. Failure Modes and How the System Handles Them

### Hot partitions and large channels

The skewed channel distribution means a handful of giant public-server channels produce outsized write bursts. This is the irreducible tension of channel-partitioned chat: the partition key that makes reads cheap concentrates writes.

- **Detection**: per-partition write rates and per-node load skew; one bucket's owners running hotter than cluster average.
- **Structural mitigation**: time bucketing caps how large one partition can grow before traffic rolls to a fresh one.
- **Read-side mitigation**: request coalescing collapses the correlated read storm that a popular channel's open generates.
- **Residual mitigation**: cache the current bucket aggressively, and treat the very largest channels as a special operational class.

### Tombstone buildup (deletes)

Cassandra-family deletes write tombstones rather than removing data. High delete volume (moderation sweeps, spam cleanup) accumulates tombstones that reads must scan past, degrading latency until compaction clears them. Discord's 2023 post names tombstone-related read degradation as one of the operational pains of the Cassandra years.

- **Detection**: read latency climbing on partitions with heavy delete traffic; tombstone counts surfaced in query warnings.
- **Mitigation**: compaction tuning, avoiding delete-heavy patterns against hot partitions, and treating bulk moderation deletes as a planned operational event rather than a background detail.

### Garbage-collection pauses and tail latency (Cassandra era)

JVM garbage collection in Cassandra produced pauses that surfaced as p99 latency spikes, one of the explicitly stated motivations for the ScyllaDB migration. ScyllaDB's C++ shard-per-core design eliminates JVM GC and pins work to cores, which is the architectural (not merely configurational) fix.

### Compaction pressure

Append-heavy workloads generate continuous compaction work in LSM-family stores; falling behind means more files per read and degrading latency, and compaction itself competes with live traffic for disk I/O. The operational lesson Discord's posts underline: compaction strategy and throughput headroom are first-order capacity questions, not tuning afterthoughts.

### Repair and anti-entropy cost

Repairs (reconciling replicas) in large Cassandra clusters were described as slow, expensive, and risky operations that operators came to dread. Skipping repair invites silent replica divergence; running it hurts production. This dread was part of the migration's motivation, and the lesson is that repair ergonomics belong in the database-selection rubric.

### Correlated-read storms

A popular channel opening on thousands of clients at once is a read thundering herd. Without coalescing, each client triggers its own query; with the Rust data-services layer, identical concurrent queries share one database round trip.

## 6. What the Migration Teaches About Operations

The 2023 migration is, at its core, an operations case study.

- **Compaction**: append-only message streams live or die by compaction behavior. Choose and monitor compaction as a capacity decision; a cluster that cannot compact faster than it ingests is on a countdown.
- **GC pauses**: a garbage-collected storage engine exports its pause distribution straight into your user-facing p99. When tail latency is the product (a channel that "feels instant"), runtime choice is a product decision.
- **Repair**: anti-entropy is the tax on replication. If running repair endangers the cluster and skipping it endangers correctness, the engine is taxing you in the worst place.
- **Replaceability**: the migration was cheap *relative to its scale* because the model, the query interface, and the client contract stayed fixed. Boundaries you draw early are what make engines replaceable later.

## 7. Monitoring and Operational Signals

For a message store at this scale, the dashboard shortlist follows directly from the failure modes:

- Per-partition and per-node write/read rates, watched for skew rather than averages.
- Read latency percentiles, especially p99, split by current-bucket versus scroll-back reads.
- Tombstone counts encountered per read, and compaction backlog (files pending merge).
- Coalescing effectiveness: ratio of client queries to issued database queries in the data-services tier.
- Cache hit rate on current buckets; a miss storm here is the first symptom of a correlated-read event.
- Storage growth rate versus forecast, because unbounded retention makes capacity planning a standing discipline rather than an annual review.
- Replica lag and repair duration, the early-warning pair for anti-entropy trouble.
- Migration-era only: divergence rate between old and new stores on dark reads, and fallback frequency.

## 8. Trade-offs Made

| Axis | Choice made | Cost accepted |
|---|---|---|
| Retention vs storage cost | Keep everything, forever | Monotonic storage growth; no expiry lever |
| Read latency vs write fan-out | Channel+time partitioning | Write concentration on hot channels |
| Ordering vs simplicity | Time-ordered Snowflake IDs | Clock-discipline requirements; ID format lock-in |
| Engine change vs model change | New engine (ScyllaDB), same model | A live migration at trillion-message scale |
| Consistency vs availability | Tunable, favoring availability for reads | Occasional stale or out-of-order edge cases |
| Operational effort vs tail latency | Managed C++ engine + Rust tier | Two specialized stacks to staff and run |

## 9. Lessons Learned

1. **Design the partition scheme for the skew, not the average.** Average channel sizes are irrelevant; the largest channels define the worst case.
2. **Bound every partition.** Unbounded partitions are unbounded incidents; time buckets convert growth into rotation.
3. **When the pain is operational, change the engine before the model.** Discord's data model survived both migrations intact; GC pauses, repair dread, and compaction behavior were engine properties.
4. **Correlated reads deserve a coalescing tier.** At chat scale, the same query repeated thousands of times per second is the normal case, not an edge case.
5. **Deletes are not free in LSM-family stores.** Tombstones are deferred work billed to future reads; treat bulk deletion as a design event.
6. **Keep launch architecture honest but simple.** The early MongoDB phase was right for its stage; what made the later migrations possible was that the write path stayed conceptually simple.
7. **Publish your scars.** Both source posts are detailed post-mortems of operational pain; they are now the standard reference for chat storage design, which compounds the engineering brand value of doing the work.

## 10. Interview Relevance

### Question 1: "Design message storage for a chat service at massive scale."

Lead with the partition decision: messages partitioned by channel and a rolling time bucket, with time-ordered IDs so ordering and pagination are free. State why: the dominant read is recent per-channel history, and bounding partition size is the only way retention can be unbounded. Then name the skew problem (mega-channels) as the primary residual risk, which shows you designed for reality, not averages. Reference Discord's published architecture as evidence the shape works at trillion-message scale. A weak answer starts from database brands; a strong one starts from the read pattern.

### Question 2: "A celebrity channel is creating a hot partition. What are your options?"

First, contain: time buckets already cap how bad one partition can get, and request coalescing collapses the correlated read storm. Second, reduce load on the owning nodes: aggressive caching of the current bucket, and rate limiting for non-critical consumers. Third, structural options if the channel is persistently extreme: shorten the bucket window for that channel's class, or split the channel's active writes across sub-partitions with a merge at read time, accepting read-side complexity. The weak answer is "add more nodes", because one partition's traffic cannot be spread by adding nodes that do not own it. Interviewers use this question to check whether you understand partition ownership at all.

### Question 3: "Your database's p99 is spiking and you suspect the JVM. Walk through the decision."

Quantify first: correlate pauses with GC logs and read latency. If GC is the cause, the ladder is tuning (heap sizing, GC algorithm), workload shaping (reduce tombstones and compaction pressure), and finally engine replacement. Discord's published migration is the canonical endpoint of that ladder: after years of tuning Cassandra, they moved to ScyllaDB specifically because shard-per-core C++ removes JVM GC structurally, and they kept the data model to keep the migration tractable. The interview signal is knowing that "rewrite the database layer" can be the *conservative* option when the data model stays fixed. A weak answer jumps to replacement without the tuning and workload-shaping rungs.

### Question 4: "What is request coalescing, and when does it break?"

Coalescing deduplicates identical concurrent queries: the first requester triggers the database call, concurrent identical requests attach to it, and all receive the same response. It shines when reads are correlated (a popular channel's recent messages) and turns a thundering herd into one query. It breaks when requests are not actually identical (different pagination cursors or auth-scoped results), when the coalesced key space is so large that the bookkeeping costs more than the queries, and for writes, where coalescing would change semantics. Saying where it fails is worth more than describing where it works. A weak answer treats coalescing as a cache, which it is not: it deduplicates work in flight, not results over time.

## 11. Capacity Arithmetic (Labelled Estimates)

Illustrative only; not company figures. Suppose 1 billion messages/day:

- Write rate: ~1e9 / 86400 ~ 12,000 messages/second average, with peak several times average.
- Payload: at ~100 bytes/message, ~100 GB/day raw; with replication factor 3 plus compaction headroom, plan for roughly 3-6x that in daily storage growth.
- Yearly: ~36 TB raw payload, low hundreds of TB replicated, before metadata and indexes.
- Read side: if the average written message is read within the hour by ~5 channel members, recent-message reads run at several times the write rate, almost all against current buckets, which is why coalescing and caching the hot set matter more than raw disk.

The design conclusion the arithmetic supports: average throughput is modest; the problems are skew (hot channels), tail latency (p99), and unbounded retention.

## 12. Contrast: Discord vs WhatsApp Storage Philosophy

Both are chat systems, but the products differ, and the storage follows:

| Aspect | Discord (this study) | WhatsApp (companion case study) |
|---|---|---|
| Core product | Persistent group channels with infinite scroll-back | Personal/small-group messaging |
| History retention | Indefinite, server-side, browsable | Primarily device-side; server holds until delivery |
| Dominant read | Recent per-channel history, many readers | Per-recipient pending message delivery |
| Storage shape | Partitioned shared history (channel, bucket) | Per-user message queues (published descriptions) |
| Hot spot | Mega-channels with many concurrent readers | Fan-out bursts to large group membership |

Same industry, opposite gravity: Discord centralizes history for many readers; WhatsApp pushes messages out to devices and largely gets out of the way. Interviewers love the comparison because it proves the schema follows the product.

### A Fair Question: Why Not a Time-Series Database?

Messages are timestamped and append-only, so TSDBs look tempting, and the time-bucketed storage shape is genuinely similar. The differences are read semantics and payload: chat reads need per-channel ordered slices of whole messages with exact pagination, while TSDBs optimize for metric aggregation and downsampling over series. The bucket idea transfers; the engine's query model does not. This is worth mentioning in an interview precisely because it shows the difference between borrowing a storage *shape* and borrowing a storage *engine*.

## 13. Related Repo Content

- [Chat/Messaging Service HLD](../../04-hld-projects/chat-service/) — the project template this case study grounds.
- [WhatsApp Messaging Case Study](../whatsapp-messaging/) — a different set of answers (Erlang, offline queueing) to the same class of problem.
- [Database Sharding (HLD)](../../03-hld-concepts/database-sharding/) — partitioning strategy and hot-key analysis.
- [NoSQL Databases (HLD)](../../03-hld-concepts/nosql-databases/) — where Cassandra-family stores fit.
- [Time Series Databases (HLD)](../../03-hld-concepts/time-series-databases/) — the same append-only, time-bucketed storage shape in another domain.

## 14. Glossary for This Case Study

- **Snowflake ID**: a time-ordered unique ID embedding a timestamp, popularized by Twitter; ordering and bucketing fall out of the ID.
- **Time bucket**: a fixed window of a channel's history stored as one partition; bounds partition growth.
- **Tombstone**: a deletion marker in LSM-family stores; reads skip over it until compaction removes it.
- **Request coalescing**: deduplicating identical concurrent queries so only one reaches the database.
- **Shard-per-core**: an architecture pinning data and work to CPU cores to avoid cross-core locking, used by ScyllaDB.
- **Anti-entropy repair**: background reconciliation between replicas holding the same data.

## 15. Summary

Discord's message storage story is three decisions compounding over eight years of published evolution:

1. **Model**: time-ordered IDs plus `(channel, time bucket)` partitioning made unbounded retention compatible with bounded partitions.
2. **Access**: a Rust data-services tier with request coalescing made correlated chat reads cheap without touching the model.
3. **Engine**: ScyllaDB replaced Cassandra to remove JVM and repair pain while the model and query interface stayed fixed.

The meta-lesson for interviews and for real systems: durable architectures are the ones whose layers can be replaced independently, and this case study is a published example of a company replacing every layer except the one that was already right.

## 16. Sources

- "How Discord Stores Billions of Messages", Discord Engineering Blog, 2017 — the Cassandra data model: Snowflake-style IDs, channel-and-time-bucket partitioning, the move off the launch database.
- "How Discord Stores Trillions of Messages", Discord Engineering Blog, 2023 — the ScyllaDB migration, the Rust data-services layer, request coalescing, and the operational motivations (GC pauses, repair cost, tombstones).

All specific figures in this case study ("billions" in 2017, "trillions" in 2023) come from these two posts. Everything else numeric is either qualitative or a labelled estimate with its arithmetic shown. No text was copied from the sources.
