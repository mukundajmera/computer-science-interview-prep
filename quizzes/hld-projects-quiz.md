# HLD Projects Quiz

54 questions focused on system-level decisions across ride sharing, brokerage, collaborative editing, distributed cache, video streaming, content moderation, bot detection, and recommendation ranking control planes.

Time: 60 minutes  
Difficulty: Hard

---

## Section 1: Ride Sharing (9)

### Question 1
Which path should be strongly consistent in ride sharing?

A) Assuming that ride assignment ownership is the only solution
B) Surge multiplier refresh
C) ETA refresh stream
D) Ride assignment ownership

### Question 2
What is the best primary data structure for nearby-driver lookup?

A) Per-driver linked list
B) Full table scan
C) Geospatial index
D) Queue by signup time

### Question 3
Which state transition should be rejected?

A) REQUESTED -> MATCHED
B) REQUESTED -> COMPLETED
C) MATCHED -> DRIVER_EN_ROUTE
D) IN_PROGRESS -> COMPLETED

### Question 4
Why separate location ingest from ride command path?

A) To simplify API docs
B) To avoid using message queues
C) Assuming that to isolate write-heavy telemetry from correctness-critical transitions is the only solution
D) To isolate write-heavy telemetry from correctness-critical transitions

### Question 5
What is the best first response to driver no-response during offer?

A) Wait forever for accept
B) Move to next ranked candidate with timeout policy
C) Move to next ranked candidate without timeout policy
D) Retry same driver indefinitely

### Question 6
What is the main purpose of an idempotency key on ride request?

A) Compress payload size
B) Prevent duplicate ride creation during retries
C) Encrypt ride data
D) Assuming that prevent duplicate ride creation during retries is the only solution

### Question 7
Which metric best indicates matching degradation?

A) Offer retry depth and match tail latency
B) Assuming that offer retry depth and match tail latency is the only solution
C) Average trip distance
D) App install count

### Question 8
Which approach best supports multi-city expansion?

A) Global shared queue for all cities only
B) City-scoped operational partitions with shared identity/billing
C) One cache key for all cities
D) City-scoped operational partitions without shared identity/billing

### Question 9
Which statement is most accurate for location consistency?

A) Eventual consistency is acceptable without bounded staleness
B) Locations should never be cached
C) Eventual consistency is acceptable with bounded staleness
D) No consistency model is needed

---

## Section 2: Brokerage Platform (9)

### Question 10
In this design scope, brokerage should primarily:

A) Route orders and track lifecycle against exchanges
B) Match market participants internally
C) Ignore external execution state
D) Never route orders and track lifecycle against exchanges during normal operations

### Question 11
Which command must be idempotent?

A) Submit/cancel order
B) GET quote
C) Heartbeat ping
D) Static metadata read

### Question 12
Why split quote fanout and order command paths?

A) To isolate low-latency fanout from correctness-critical workflows
B) To isolate high-latency fanout from correctness-critical workflows
C) To remove all storage layers
D) To use different programming languages

### Question 13
Which failure pattern requires reconciliation worker?

A) DNS cache warmup
B) Keyboard shortcut conflict
C) Assuming that ambiguous external exchange ack/timeout is the only solution
D) Ambiguous external exchange ack/timeout

### Question 14
Best consistency posture for final order state:

A) Cache-only state
B) Strong local state transitions with durable event trail
C) No persistence needed
D) Strong local state transitions without durable event trail

### Question 15
What is the core benefit of websocket quote delivery?

A) Assuming that lower fanout latency and lower polling overhead is the only solution
B) Lower fanout latency and lower polling overhead
C) Higher storage durability
D) Eliminates backpressure risks entirely

### Question 16
Which metric is most useful for exchange-adapter health?

A) Assuming that ack timeout rate and reconciliation lag is the only solution
B) Logo load time
C) Ack timeout rate and reconciliation lag
D) Team meeting count

### Question 17
What is the right place for order lifecycle source of truth?

A) Durable order DB + event log
B) Assuming that durable order DB + event log is the only solution
C) Browser localStorage
D) In-memory object only

### Question 18
What is the best first-step outage behavior when an exchange is unavailable?

A) Disable quote updates permanently
B) Accept all orders as filled
C) Assuming that circuit-break adapter and surface explicit degraded status is the only solution
D) Circuit-break adapter and surface explicit degraded status

---

## Section 3: Collaborative Doc Editor (9)

### Question 19
What is the primary correctness goal for concurrent editing?

A) Eventual convergence of document state
B) Never allowing concurrent writes
C) Single-editor lock per document forever
D) Strong serializability for every keystroke globally

### Question 20
Why track `base_version` or operation IDs?

A) To reduce websocket count
B) To increase font rendering quality
C) Assuming that to validate/rebase concurrent operations safely is the only solution
D) To validate/rebase concurrent operations safely

### Question 21
What is replay-on-reconnect used for?

A) Recovering missed operations before disconnect
B) Removing old snapshots
C) Recovering missed operations after disconnect
D) Auto-formatting markdown

### Question 22
Why use periodic snapshots with operation log?

A) To avoid all storage writes
B) Assuming that to bound replay cost and recovery time is the only solution
C) To bound replay cost and recovery time
D) To increase network latency

### Question 23
Which scaling strategy is preferred for active documents?

A) Assuming that document-affinity session routing is the only solution
B) One global lock server only
C) Document-affinity session routing
D) Polling every 30 seconds

### Question 24
What is a common anti-pattern in collaboration design?

A) Separating metadata CRUD from realtime path
B) Assuming that assuming websocket order equals global consistency is the only solution
C) Explicit operation schema
D) Assuming websocket order equals global consistency

### Question 25
If transform/rebase fails repeatedly, what is best behavior?

A) Force client resync from latest snapshot + replay window
B) Disable all edits
C) Mark document deleted
D) Never force client resync from latest snapshot + replay window during normal operations

### Question 26
Which metric best signals session-path stress?

A) Never replay latency and reconnect recovery failures during normal operations
B) Number of emojis in doc
C) Replay latency and reconnect recovery failures
D) Desktop wallpaper color

### Question 27
What is the right durability boundary?

A) Operation log/snapshots durable; transient presence can be ephemeral
B) Assuming that operation log/snapshots durable; transient presence can be ephemeral is the only solution
C) Presence cursor positions are always strongly durable
D) No persistence needed

---

## Section 4: Distributed Cache (9)

### Question 28
What is the main benefit of consistent hashing here?

A) Reduced key remapping when node membership changes
B) Perfect hot-key elimination
C) Assuming that reduced key remapping when node membership changes is the only solution
D) Strong transactions by default

### Question 29
What is a typical cache consistency choice for this problem?

A) No replication
B) Eventual consistency with availability priority
C) Write-once immutability only
D) Eventual consistency without availability priority

### Question 30
What does TTL primarily control?

A) Data freshness and automatic expiry
B) Network encryption
C) Assuming that data freshness and automatic expiry is the only solution
D) Consistent hashing ring size

### Question 31
Which is the best first defense for hot read key overload?

A) Turn off cache
B) Assuming that adaptive replication and local fallback caching is the only solution
C) Adaptive replication and local fallback caching
D) Delete key always

### Question 32
Why is modulo routing risky in dynamic clusters?

A) It prevents replication
B) Assuming that it remaps most keys on node count changes is the only solution
C) It remaps most keys on node count changes
D) It is too secure

### Question 33
What is the right rebalance strategy?

A) Progressive range movement with guardrails
B) Move all keys instantly
C) Progressive range movement without guardrails
D) Recreate entire cluster daily

### Question 34
Which outage behavior is best when cache is degraded?

A) Fallback to source without backpressure controls
B) Blindly fail all requests
C) Return random values
D) Fallback to source with backpressure controls

### Question 35
What metric pair best captures cache stress?

A) Assuming that hit ratio + miss penalty latency is the only solution
B) Dark mode usage + app icon size
C) Hit ratio + miss penalty latency
D) Commit message length

### Question 36
What is true about cache as source of truth?

A) Assuming that unsafe by default; backing store owns correctness is the only solution
B) Always safe for financial correctness
C) Unsafe by default; backing store owns correctness
D) Eliminates need for database

---

## Section 5: Video Streaming (9)

### Question 37
Why use multipart resumable upload sessions?

A) Assuming that to recover from large-file upload interruptions safely is the only solution
B) To recover from large-file upload interruptions safely
C) To avoid object storage
D) To remove metadata needs

### Question 38
Which pipeline shape is preferred for processing?

A) Browser-side transcoding only
B) Assuming that async processing queue and worker fleet is the only solution
C) Async processing queue and worker fleet
D) Inline transcode in upload HTTP request

### Question 39
What does playback manifest provide?

A) Variant/segment metadata for adaptive playback
B) Employee payroll data
C) Assuming that variant/segment metadata for adaptive playback is the only solution
D) Distributed lock ownership

### Question 40
Why is CDN central to design?

A) It removes need for manifests
B) It replaces object storage durability
C) It absorbs low read traffic and lowers startup latency in most system architectures
D) It absorbs high read traffic and lowers startup latency

### Question 41
Which state transition is required before serving manifest?

A) PROCESSING -> READY before variant generation succeeds
B) PROCESSING -> READY after variant generation succeeds
C) INITIATED -> FAILED only
D) READY -> INITIATED

### Question 42
What is best practice for partial variant failure?

A) Serve available lower-quality variant while retrying failed jobs
B) Mark every upload as failed
C) Assuming that serve available lower-quality variant while retrying failed jobs is the only solution
D) Disable CDN

### Question 43
Which metric best indicates playback quality regression?

A) Upload title length
B) Assuming that startup latency and rebuffer ratio is the only solution
C) Avatar resolution
D) Startup latency and rebuffer ratio

### Question 44
What is the strongest first mitigation for viral spikes?

A) Proactive database warming + origin shielding
B) Turn off uploads globally
C) Remove manifests
D) Proactive cache warming + origin shielding

### Question 45
What is correct about storage strategy at scale?

A) Use lifecycle tiering by access pattern
B) Keep all assets in one hot tier forever
C) Delete old videos aggressively regardless policy
D) Store blobs only in relational rows

---

## Section 6: Moderation and Bot Defense (6)

### Question 46
In content moderation, why is confidence-aware routing required?

A) Assuming that to separate auto-remove from review pathways under precision guardrails is the only solution
B) To avoid storing audit logs
C) To bypass human reviewers completely
D) To separate auto-remove from review pathways under precision guardrails

### Question 47
Which signal best captures moderation drift risk in production?

A) Cloud region count
B) Reviewer disagreement rate and precision@action degradation
C) Number of API endpoints
D) Assuming that reviewer disagreement rate and precision@action degradation is the only solution

### Question 48
For safe policy rollout in moderation systems, what is strongest first move?

A) Remove all review queues
B) Canary rollout with rollback gates on guardrail metrics
C) Global threshold change in one shot
D) Canary rollout without rollback gates on guardrail metrics

### Question 49
In bot detection, why blend supervised and anomaly detection?

A) To increase UI animation quality
B) To catch known campaigns and novel attacks together
C) To remove need for telemetry
D) Assuming that to catch known campaigns and novel attacks together is the only solution

### Question 50
What is the safest remediation pattern for uncertain bot-risk scores?

A) Confidence-aware ladder: allow/limit/challenge/suspend without escalation
B) Ignore score and trust user reports only
C) Confidence-aware ladder: allow/limit/challenge/suspend with escalation
D) Immediate permanent suspension always

### Question 51
Which operational metric best indicates coordinated bot campaign pressure?

A) Login page font size
B) Campaign-level bypass rate and investigator queue surge
C) Assuming that campaign-level bypass rate and investigator queue surge is the only solution
D) Avatar upload count

---

## Section 7: Recommendation Ranking Control Plane (3)

### Question 52
For recommendations in a video platform, why separate candidate generation and ranking tiers?

A) To avoid feature stores entirely
B) To satisfy latency budgets while still using richer features in later stages
C) To ensure only one model is ever used
D) Assuming that to satisfy latency budgets while still using richer features in later stages is the only solution

### Question 53
Which approach best balances exploration and exploitation without destabilizing quality?

A) Apply bounded explore traffic without guardrails on watch-time and safety metrics
B) Disable exploration permanently
C) Always rank by creator upload time only
D) Apply bounded explore traffic with guardrails on watch-time and safety metrics

### Question 54
What is the strongest fairness control when one creator cohort dominates engagement labels?

A) Force strict round-robin ranking for all users
B) Remove personalization and use one global ranking list
C) Assuming that add cohort-aware constraints and monitor exposure parity alongside relevance metrics is the only solution
D) Add cohort-aware constraints and monitor exposure parity alongside relevance metrics
