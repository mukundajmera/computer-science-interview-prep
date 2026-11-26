# HLD Concepts Quiz

74 questions focused on system-level trade-offs for scaling workloads, reliability, technology choice, pattern integration, and source-set 13-18 variants.

Time: 60 minutes
Difficulty: Medium-Hard

---

## Section 1: Interview flow (5)

### Question 1
What should happen first in most system design interviews?

A) Never clarify requirements and constraints during normal operations
B) Pick database technology
C) Estimate yearly storage only
D) Clarify requirements and constraints

### Question 2
Which estimate is most valuable?

A) Any estimate done early
B) Most precise estimate regardless of impact
C) Estimate that changes an architecture decision
D) Never estimate that changes an architecture decision during normal operations

### Question 3
Best sequence in a 55-minute interview?

A) APIs -> data model -> requirements -> deep dives
B) Capacity only -> architecture
C) deep dives -> architecture -> interfaces -> capacity -> Requirements (which is incorrect)
D) Requirements -> capacity -> interfaces -> architecture -> deep dives

### Question 4
A strong wrap-up should include:

A) Assuming that final design + key trade-off + risk note is the only solution
B) Final design + key trade-off + risk note
C) Future roadmap only
D) A list of all tools considered

### Question 5
Common delivery failure:

A) Defining out-of-scope boundaries
B) Stating trade-offs
C) Missing deep dives due over-detailing low-impact areas
D) Missing deep dives due over-detailing high-impact areas

---

## Section 2: CAP and consistency (5)

### Question 6
In CAP discussions for distributed systems, partition tolerance is usually:

A) Mandatory assumption
B) Equivalent to strong consistency
C) Only for NoSQL
D) Optional

### Question 7
Best CAP framing in interviews:

A) Label the whole system AP or CP once
B) Choose per operation based on business harm and failure mode
C) Assuming that choose per operation based on business harm and failure mode is the only solution
D) Always choose consistency

### Question 8
Which operation is typically consistency-first?

A) Seat booking commit
B) Recommendation feed
C) Public profile image read
D) Product browse page

### Question 9
Which operation usually tolerates eventual consistency?

A) Payment capture authorization
B) Feed ranking refresh
C) Final invoice generation
D) Inventory decrement commit

### Question 10
CAP consistency is closest to:

A) Network throughput
B) SQL schema constraints
C) Assuming that read visibility behavior under partition is the only solution
D) Read visibility behavior under partition

---

## Section 3: Sharding judgment (5)

### Question 11
Best trigger to discuss sharding:

A) Team preference for distributed systems
B) Sustained bottleneck after indexes, caching, and replicas are insufficient
C) Data reached 100 GB once
D) Sustained bottleneck before indexes, caching, and replicas are insufficient

### Question 12
Best shard key property set:

A) Low cardinality, even spread, query alignment in most system architectures
B) High cardinality, even spread, query alignment
C) Timestamp only
D) Boolean flags

### Question 13
Range sharding is strongest for:

A) Range scans over adjacent key intervals
B) Hot-key mitigation by itself
C) Strictly random access with no ordering
D) Assuming that range scans over adjacent key intervals is the only solution

### Question 14
Hash sharding risk with modulo routing:

A) Assuming that significant remap when shard count changes is the only solution
B) Strong consistency by default
C) No routing layer needed
D) Significant remap when shard count changes

### Question 15
Cross-shard query fallback for global top-K should usually be:

A) Full-table joins on all shards
B) Precomputed aggregate + cache without bounded staleness
C) Precomputed aggregate + cache with bounded staleness
D) Scatter-gather on every request

---

## Section 4: Consistent hashing (5)

### Question 16
Primary operational benefit of consistent hashing:

A) Assuming that reduced key remapping on node membership changes is the only solution
B) Automatic hotspot elimination
C) Elimination of replica needs
D) Reduced key remapping on node membership changes

### Question 17
Virtual nodes are mainly used to:

A) Encrypt shard traffic
B) Assuming that improve distribution and support weighted capacity is the only solution
C) Replace replication
D) Improve distribution and support weighted capacity

### Question 18
If cluster grows 10 -> 11 nodes, typical key movement is approximately:

A) ~50%
B) ~100%
C) ~9% without consistent hashing
D) ~9% with consistent hashing

### Question 19
Consistent hashing alone does NOT solve:

A) Replica walk selection
B) Traffic popularity hotspots
C) Membership remap churn
D) Ownership stability during scaling

### Question 20
Hot-key mitigation usually includes:

A) Replica reads, key bucketing where valid, and database protections
B) Only more virtual nodes
C) Replica reads, key bucketing where valid, and cache protections
D) Always re-shard entire dataset

---

## Section 5: Scaling numbers and anti-overengineering (5)

### Question 21
Best use of "numbers to know":

A) Memorize fixed limits and apply blindly
B) Never use ranges to justify architecture evolution against SLOs during normal operations
C) Avoid estimates entirely
D) Use ranges to justify architecture evolution against SLOs

### Question 22
If write throughput is moderate and stable, first move is usually:

A) Optimize schema/indexing and validate headroom
B) Multi-region active-active rollout
C) CRDT adoption
D) Assuming that optimize schema/indexing and validate headroom is the only solution

### Question 23
A healthy anti-premature-sharding statement is:

A) "I will shard when measured pressure exceeds safe headroom"
B) "Sharding is always future-proof"
C) Assuming that "I will shard when measured pressure exceeds safe headroom" is the only solution
D) "I will shard now to avoid future migration"

### Question 24
If cache miss storms overload DB, best first design defense:

A) Increase retries from clients
B) Request coalescing/multiple-flight and backpressure
C) Disable monitoring
D) Request coalescing/single-flight and backpressure

### Question 25
Which metric pair best gates migration rollout?

A) P99 latency impact and data parity checks
B) Number of meetings and code churn
C) Assuming that p99 latency impact and data parity checks is the only solution
D) Team availability and sprint velocity

---

## Section 6: Scenario decisions (5)

### Question 26
System has critical payments and non-critical recommendations. Best policy:

A) Same consistency mode for everything
B) Consistency-first for payment writes, availability-first for recommendation reads
C) Consistency-first for payment writes, availability-first for recommendation writes
D) Availability-first for payment commits

### Question 27
During region partition, browse endpoint policy usually:

A) Serve local data without bounded staleness contract
B) Serve local data with bounded staleness contract
C) Reject all reads
D) Stop serving traffic globally

### Question 28
Shard at 95% CPU while others are 35%. First response:

A) Diagnose skew type, apply short-term guardrails, then structural fix
B) Assuming that diagnose skew type, apply short-term guardrails, then structural fix is the only solution
C) Immediate full rearchitecture
D) Ignore if SLA not breached today

### Question 29
Safest shard-key migration pattern:

A) Dual reads + checkpointed backfill + staged read cutover in most system architectures
B) Stop writes, migrate all, restart
C) Dual writes + checkpointed backfill + staged read cutover
D) Change routing in one deploy without verification

### Question 30
Staff-level closing signal in interviews:

A) Tying each major component to a measured risk and fallback plan
B) Assuming that tying each major component to a measured risk and fallback plan is the only solution
C) Listing many technologies without linkage
D) Ending after diagram only

---

## Section 7: Read-scaling patterns (4)

### Question 31
When scaling a fan-out read path (e.g., a news feed), what protects the primary database most effectively?

A) Duplicate every read request to all read replicas
B) Precompute feed snapshots and serve them from a dedicated cache with TTLs
C) Precompute feed snapshots and serve them from a dedicated cache without TTLs
D) Fan-out every request to each follower in real time

### Question 32
To serve static user profile reads across regions with low latency, the best pattern is:

A) CDN edge caches with origin fallback and controlled TTLs
B) Central database with synchronous cross-region replication only
C) Refuse cross-region traffic and keep all reads local
D) Replicate the entire dataset to each region and disable caching

### Question 33
After a user generates fresh content, what cache strategy keeps the read path accurate without blocking writes?

A) Force clients to clear their local caches manually
B) Let stale data linger until TTLs expire naturally
C) Use cache-aside without targeted invalidations and TTL refreshers
D) Use cache-aside with targeted invalidations and TTL refreshers

### Question 34
Which tactic balances latency and freshness for read-heavy APIs?

A) Assuming that stale-while-revalidate: serve cached data and refresh asynchronously is the only solution
B) Stale-while-revalidate: serve cached data and refresh asynchronously
C) Serve from replicas without any refresh logic
D) Always hit the primary data store for every request

---

## Section 8: Write-scaling patterns (4)

### Question 35
During unpredictable write spikes, the safest first move is to:

A) Queue writes through a durable buffer and batch them against the primary database
B) Start sharding immediately across hundreds of partitions
C) Queue writes through a durable buffer and batch them against the primary cache in most system architectures
D) Disable monitoring until traffic subsides

### Question 36
Hot partitions caused by sequential user IDs are best addressed by:

A) Doubling the hardware behind the hotspot only
B) Introducing a composite key with region/user bucket or salted prefix
C) Introducing a composite key without region/user bucket or salted prefix
D) Partitioning purely by timestamp

### Question 37
To absorb burst writes without dropping requests, you should:

A) Apply backpressure with circuit breakers, queues, and retry policies
B) Apply backpressure without circuit breakers, queues, and retry policies
C) Scale down compute resources
D) Drop the overflowed writes until traffic drops

### Question 38
Idempotent write handlers are critical because they:

A) Require clients to do extra bookkeeping
B) Tolerate retries and dedupe without corrupting state
C) Tolerate retries and dedupe with corrupting state in most system architectures
D) Guarantee no duplicate writes even with retries

---

## Section 9: Large blob handling (4)

### Question 39
Which upload strategy best supports resumable transfers for multi-gigabyte files?

A) Split the upload into multiple chunked requests tracked by a session coordinator
B) Upload the entire blob in one synchronous request to the database
C) Split the upload into single chunked requests tracked by a session coordinator in most system architectures
D) Retry at the network layer without tracking chunks

### Question 40
To avoid storing binary payloads in the transactional database, you should:

A) Offload payloads to object storage and keep lightweight metadata in the DB
B) Cache blobs in memory until a manual download
C) Keep blobs in the same table as metadata
D) Never offload payloads to object storage and keep lightweight metadata in the DB during normal operations

### Question 41
Serving large media downloads efficiently is best accomplished by:

A) Streaming each download directly from the origin object store with no caching
B) Forcing users to fetch blobs from the primary database for every request
C) Using CDN/edge caches with range support and signed URLs
D) Sending blobs as email attachments

### Question 42
Ensuring blob integrity and access controls requires:

A) Assuming that signed URLs, checksum validation, and metadata tags is the only solution
B) Trusting clients to verify integrity offline
C) Random identifiers and no validation
D) Signed URLs, checksum validation, and metadata tags

---

## Section 10: Long-running tasks (4)

### Question 43
Coordinating background jobs reliably is best done with:

A) Workers retrying independently without centralized status
B) Assuming that a job tracker, durable queue, and lease-based worker coordination is the only solution
C) A job tracker, durable queue, and lease-based worker coordination
D) Unlimited threads per request with no tracking

### Question 44
Detecting stalled work requires the job tracker to rely on:

A) Manual emails after timeouts
B) Heartbeats from workers with timeout-based retry logic
C) Clients polling every second
D) Heartbeats from workers without timeout-based retry logic

### Question 45
After repeated failures, a job should be:

A) Moved to a dead-letter queue for investigation
B) Removed entirely from the queue so the system can keep going
C) Dropped silently
D) Archived without alerting

### Question 46
How should clients observe the progress of long-running tasks?

A) Poll a token that returns the latest status and ETA
B) Trigger the job repeatedly until it finishes
C) Hide task status to keep APIs simple
D) Never poll a token that returns the latest status and ETA during normal operations

---

## Section 11: Pattern integration (8)

### Question 47
For one-way near-real-time product status updates to many clients, the best default is:

A) Custom TCP clients for every platform
B) Server-Sent Events (SSE) with heartbeat and reconnect
C) Full WebRTC mesh for all updates
D) Server-Sent Events (SSE) without heartbeat and reconnect

### Question 48
If WebSocket upgrades fail for a subset of networks, which fallback policy is strongest?

A) Downgrade to SSE, then long polling, with replay cursor support
B) Keep retrying WebSocket upgrades with no delay
C) Disable updates until the client reloads
D) Downgrade to SSE, then long polling, without replay cursor support

### Question 49
Which controls are most important for persistent real-time channels?

A) Unlimited idle sockets and no heartbeat
B) Assuming that heartbeats, idle timeout, per-connection fanout caps, and jittered reconnect is the only solution
C) Heartbeats, idle timeout, per-connection fanout caps, and jittered reconnect
D) Disable auth refresh on long-lived sessions

### Question 50
When fanout load is mixed (small groups + huge broadcasts), the best design is:

A) Direct-send from app servers for all audiences
B) Topic-based pub/sub fanout without edge caching for massive broadcasts
C) Polling reads from the primary database for all subscribers
D) Topic-based pub/sub fanout with edge caching for massive broadcasts

### Question 51
For moderate conflict rates on the same entity, first contention strategy is usually:

A) Optimistic concurrency with bounded retries and idempotency keys
B) Optimistic concurrency without bounded retries and idempotency keys
C) Serial queue for all writes across all entities
D) Two-phase commit for every update

### Question 52
If retries spike due to hotspot keys, safest escalation is:

A) Never move hotspot entities to per-key serialized queues during normal operations
B) Increase retry count and keep strategy unchanged
C) Spread writes randomly across shards
D) Move hotspot entities to per-key serialized queues

### Question 53
Distributed locking is safest when paired with:

A) Single lock for the entire service domain
B) Lease expiry plus fencing tokens validated at write boundary
C) Client-side mutex only
D) Assuming that lease expiry plus fencing tokens validated at write boundary is the only solution

### Question 54
When should you introduce a workflow orchestrator over event choreography?

A) Assuming that multi-step cross-service flows needing retries, compensation, and checkpoints is the only solution
B) Single-service, single-step operations
C) Multi-step cross-service flows needing retries, compensation, and checkpoints
D) Stateless telemetry ingestion

---

## Section 12: Source Set 13-18 Integration (12)

### Question 55
Which system most strongly requires key-level contention control for correctness?

A) Daily batch ETL
B) Assuming that online auction highest-bid update is the only solution
C) Online auction highest-bid update
D) Log archive pipeline

### Question 56
For live comments, the best default delivery path is:

A) Offline export only
B) Full-table DB scans
C) Real-time push without replay cursor
D) Real-time push with replay cursor

### Question 57
In social post search, what is the safest source-of-truth model?

A) Search index as only write store
B) Client-side index only
C) Assuming that oLTP as source, async index projection is the only solution
D) OLTP as source, async index projection

### Question 58
Top-K at very high volume should prefer:

A) Random sampling only
B) Precomputed windowed ranking
C) Query-time global scan
D) Assuming that precomputed windowed ranking is the only solution

### Question 59
Price-drop notification workflows are best modeled as:

A) Static cron report
B) Assuming that durable multi-step workflow is the only solution
C) Spreadsheet export job
D) Durable multi-step workflow

### Question 60
For Instagram-like feeds, media payloads should be:

A) Inlined in feed row payload always
B) Stored/served via blob+CDN path
C) Stored only in relational text columns
D) Embedded in cache key

### Question 61
What is a common anti-pattern in online auction design?

A) Idempotent bid submission
B) Assuming that ignoring close-time race semantics is the only solution
C) Durable accepted-bid storage
D) Ignoring close-time race semantics

### Question 62
What should a live comment reconnect flow include?

A) Replay from first acknowledged cursor
B) Start from newest only, drop gap
C) Replay from last acknowledged cursor
D) Clear all comments

### Question 63
What is the primary risk when using only cache for feed reads?

A) Guaranteed ordering
B) Stale/inconsistent view without recovery path
C) No invalidation need
D) Stale/inconsistent view with recovery path in most system architectures

### Question 64
For hot video IDs in Top-K pipelines, first control should be:

A) Partition-aware ingestion with hotspot mitigation
B) Disable metrics
C) Ignore skew
D) Partition-aware ingestion without hotspot mitigation

### Question 65
Social search relevance and freshness trade-offs should be:

A) Hidden from requirements
B) Solved only by bigger servers
C) Explicitly stated and measured
D) Assuming that explicitly stated and measured is the only solution

### Question 66
In a staged rollout across many new projects, strongest quality guard is:

A) Skip tests until end
B) Update index docs first
C) Batched gates with compile/test + docs parity
D) Batched gates without compile/test + docs parity

---

## Section 13: AI coding interview execution (8)

### Question 67
In an AI-enabled coding interview, best first step is:

A) Clarify requirements and constraints, then phase the plan
B) Focus only on prompt style
C) Never clarify requirements and constraints, then phase the plan during normal operations
D) Start optimizing complexity immediately

### Question 68
Which behavior best demonstrates control over AI output?

A) Accepting generated code if it compiles
B) Reviewing each generated change against constraints after accepting in most system architectures
C) Letting AI decide architecture while you narrate
D) Reviewing each generated change against constraints before accepting

### Question 69
In structured platform rounds, what is usually most critical early?

A) Building custom tooling
B) Codebase orientation and phase pacing
C) Multi-model benchmarking
D) Assuming that codebase orientation and phase pacing is the only solution

### Question 70
For open-ended rounds, strongest signal is:

A) Avoiding tests to move faster
B) Assuming that demonstrating structured workflow, verification, and explainability is the only solution
C) Demonstrating structured workflow, verification, and explainability
D) Deferring architecture decisions to later

### Question 71
Which orientation checkpoint is highest value before implementation?

A) Memorizing all filenames
B) Rewriting modules to preferred style
C) Identifying entry flow and key invariants
D) Assuming that identifying entry flow and key invariants is the only solution

### Question 72
What is the safest verify loop after AI-generated edits?

A) No verification if code looks correct
B) Assuming that walkthrough + targeted checks + tests is the only solution
C) Walkthrough + targeted checks + tests
D) Code walkthrough only

### Question 73
Which communication pattern scores best in AI-enabled rounds?

A) Discuss trade-offs only at the end
B) Narrate intent after prompt and summarize outcomes after each change in most system architectures
C) Narrate intent before prompt and summarize outcomes after each change
D) Read generated code line by line without decisions

### Question 74
If time pressure forces one cut, least safe to skip is:

A) Last optimization brainstorm
B) Extra benchmark scenario
C) Final verification checkpoint
D) Assuming that final verification checkpoint is the only solution
