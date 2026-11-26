# HLD Concepts Flashcards

150 question-only flashcards for system design interview execution.

---

## Delivery Framework (8 Cards)

### Card 1
Front: What are the first three clarifications before drawing architecture?

### Card 2
Front: How do you separate functional requirements from non-functional requirements quickly?

### Card 3
Front: Which estimate is worth doing first and why?

### Card 4
Front: What is a strong 60-second interview wrap-up pattern?

### Card 5
Front: How do you declare scope boundaries without sounding defensive?

### Card 6
Front: What is the best way to state assumptions so they strengthen your answer?

### Card 7
Front: How do you decide when to switch from breadth to deep dive?

### Card 8
Front: What does a defensible architecture decision sentence sound like?

---

## CAP and Consistency (8 Cards)

### Card 9
Front: Why is partition tolerance usually treated as mandatory in distributed systems?

### Card 10
Front: How do you choose consistency vs availability per endpoint?

### Card 11
Front: Which operations in a commerce flow are consistency-first by default?

### Card 12
Front: Which operations in a social/browse flow are availability-first by default?

### Card 13
Front: How do you explain CAP consistency vs ACID consistency in one sentence?

### Card 14
Front: What is a practical degraded mode policy during region partition?

### Card 15
Front: What reconciliation details should you mention after partition heals?

### Card 16
Front: How do you communicate bounded staleness contracts in APIs?

---

## Sharding Strategy (8 Cards)

### Card 17
Front: What metrics justify moving from replicas/caching to sharding?

### Card 18
Front: What makes a shard key strong enough for production?

### Card 19
Front: When is range sharding preferable to hash sharding?

### Card 20
Front: What risks appear when using modulo-based hash sharding at scale?

### Card 21
Front: How do you reduce cross-shard query pressure on global features?

### Card 22
Front: What is your online re-sharding sequence in five steps?

### Card 23
Front: How do you describe shard-key migration with minimal downtime?

### Card 24
Front: What rollback gates should exist during re-sharding cutover?

---

## Consistent Hashing (8 Cards)

### Card 25
Front: What is the core operational benefit of consistent hashing?

### Card 26
Front: How do virtual nodes improve cluster behavior?

### Card 27
Front: Why does consistent hashing reduce remap on node changes?

### Card 28
Front: What does consistent hashing not solve by itself?

### Card 29
Front: How do you explain ring-based routing vs slot-range routing trade-offs?

### Card 30
Front: What is bounded-load consistent hashing and when does it help?

### Card 31
Front: How do you choose replica nodes on a hash ring?

### Card 32
Front: Which metrics show ring rebalance is safe to continue?

---

## Numbers and Scaling Judgment (8 Cards)

### Card 33
Front: How should "numbers to know" influence architecture choices?

### Card 34
Front: Which latency numbers are most useful in interview trade-offs?

### Card 35
Front: What throughput cues suggest queueing is warranted?

### Card 36
Front: What are anti-premature-sharding signals?

### Card 37
Front: How do you justify starting simple without sounding underprepared?

### Card 38
Front: Which metrics best indicate cache strategy is failing?

### Card 39
Front: Which metrics indicate single-primary database stress is sustained?

### Card 40
Front: How do you phrase uncertainty when ranges vary by workload?

---

## Hotspots, Failures, and Operations (8 Cards)

### Card 41
Front: What is the first triage step when one shard is overloaded?

### Card 42
Front: What short-term controls help during hot-key incidents?

### Card 43
Front: What long-term fixes prevent repeated hotspot incidents?

### Card 44
Front: How do you prevent cache stampede during rebalance?

### Card 45
Front: What should happen when a shard/node becomes unhealthy?

### Card 46
Front: How do you preserve service while recovering failed replicas?

### Card 47
Front: What observability signals matter during migration windows?

### Card 48
Front: What post-incident review outputs improve future resilience?

---

## Staff-Level Communication (8 Cards)

### Card 49
Front: How do you connect each component to a measurable risk?

### Card 50
Front: How do you explain trade-offs without sounding indecisive?

### Card 51
Front: What are red flags that your design is over-engineered?

### Card 52
Front: How do you answer "what breaks first at 10x" clearly?

### Card 53
Front: How do you defend not choosing the most complex option?

### Card 54
Front: What is a strong fallback plan statement for critical paths?

### Card 55
Front: How do you show migration safety thinking in one concise answer?

### Card 56
Front: What three closing points best signal staff-level judgment?

---

## Read-Scaling Patterns (6 Cards)

### Card 57
Front: What architecture change keeps read fan-out workloads from hitting the origin DB?

### Card 58
Front: How do you balance cache freshness with write velocity in a feed service?

### Card 59
Front: What metrics trigger CDN/edge caching for profile reads across regions?

### Card 60
Front: How do you describe the trade-off between precomputed snapshots and real-time fan-out?

### Card 61
Front: What coordination is required when promoting a cache-aside layer to the canonical read path?

### Card 62
Front: How do you measure whether read replicas are improving tail latency versus adding inconsistency risk?

---

## Write-Scaling Patterns (6 Cards)

### Card 63
Front: Which immediate control protects the primary store when writes spike unpredictably?

### Card 64
Front: How do you prevent hot partitions caused by sequential IDs without removing uniqueness?

### Card 65
Front: What role do durable queues and batching play in smoothing write bursts?

### Card 66
Front: Why do idempotent write handlers matter during retries and at-least-once delivery?

### Card 67
Front: How does backpressure and circuit breaking help keep the write path stable?

### Card 68
Front: What signals indicate it is time to split the write path along business domains or partitions?

---

## Large Blob Handling (6 Cards)

### Card 69
Front: What makes an upload session coordinator necessary for multi-gigabyte files?

### Card 70
Front: Why keep binary payloads in object storage and metadata in a relational store?

### Card 71
Front: How do CDNs and signed URLs change when serving large media downloads?

### Card 72
Front: What is the simplest way to validate blob integrity before allowing a download?

### Card 73
Front: How do you design a blob lifecycle policy that handles tiering and deletion safely?

### Card 74
Front: Which automation steps protect against orphaned chunks when a multipart upload aborts?

---

## Long-Running Tasks (6 Cards)

### Card 75
Front: How does a job tracker coordinate leases, status, and retries for background work?

### Card 76
Front: What does a heartbeat timeout reveal about stuck workers?

### Card 77
Front: In what way does an idempotency key or dedupe token keep background jobs safe from duplicates?

### Card 78
Front: How should clients monitor progress for tasks that take minutes or longer?

### Card 79
Front: What happens after a task fails repeatedly and why does it need a dead-letter queue?

### Card 80
Front: How do you expire or archive long-running job metadata without losing traceability?

---

## Real-Time Delivery Patterns (4 Cards)

### Card 81
Front: How do you choose between polling, long polling, SSE, and WebSocket for a given product interaction?

### Card 82
Front: What downgrade path should you define when WebSocket cannot be established reliably?

### Card 83
Front: Which connection-health controls are mandatory for large persistent channel fleets?

### Card 84
Front: How do you separate fanout strategy for small groups versus massive audience broadcasts?

---

## Contention Control Patterns (4 Cards)

### Card 85
Front: What signal indicates optimistic concurrency is still enough for a write path?

### Card 86
Front: When should you escalate from optimistic retries to per-key serialized queues?

### Card 87
Front: How do fencing tokens reduce stale-owner writes in distributed lock systems?

### Card 88
Front: Where should idempotency boundaries sit in high-contention workflows?

---

## Workflow Orchestration Patterns (4 Cards)

### Card 89
Front: What are practical triggers to move from choreography to a central orchestrator?

### Card 90
Front: What should a workflow step contract include for retry and compensation safety?

### Card 91
Front: How do durable checkpoints and replay make long-running flows resilient to crashes?

### Card 92
Front: How do you version workflow definitions without breaking in-flight executions?

---

## System Drills (25 Cards)

### Card 93
Front: In ride sharing, which boundary should stay strongly consistent and why?

### Card 94
Front: What makes a driver availability index different from raw online status?

### Card 95
Front: How does an offer-timeout loop improve match robustness over nearest-driver-only assignment?

### Card 96
Front: Which metrics tell you ride matching is degrading before hard outages?

### Card 97
Front: Why is idempotency mandatory on ride request and driver accept endpoints?

### Card 98
Front: In a brokerage design, what is the precise boundary between broker responsibilities and exchange responsibilities?

### Card 99
Front: Why must order command paths and quote fanout paths be separated operationally?

### Card 100
Front: What state-tracking model keeps order lifecycle recoverable after ambiguous exchange responses?

### Card 101
Front: Which health signals indicate the reconciliation loop is falling behind in brokerage systems?

### Card 102
Front: What does a safe degraded mode look like when an exchange adapter is unavailable?

### Card 103
Front: For collaborative editors, why doesn’t websocket delivery order alone guarantee correctness?

### Card 104
Front: How do base-version and operation IDs enable safe transform/rebase behavior?

### Card 105
Front: What is the minimum reconnect contract needed to avoid document divergence?

### Card 106
Front: Why combine operation logs with periodic snapshots instead of using either alone?

### Card 107
Front: Which metrics expose session-routing hot spots in document collaboration backends?

### Card 108
Front: In distributed cache design, what problem does consistent hashing solve and what does it not solve?

### Card 109
Front: Why should cluster sizing use max(memory-based, throughput-based) node estimates?

### Card 110
Front: What makes progressive rebalance safer than bulk key movement during scaling events?

### Card 111
Front: Which layered mitigations are most effective for hot-read keys?

### Card 112
Front: Why is cache fallback strategy part of correctness, not just performance?

### Card 113
Front: For video platforms, why are resumable upload sessions preferable to one-shot uploads for large files?

### Card 114
Front: Which state transitions should gate manifest availability in a video pipeline?

### Card 115
Front: Why is asynchronous processing mandatory between upload completion and playback readiness?

### Card 116
Front: Which playback SLO pair best captures user experience quality under load?

### Card 117
Front: What controls protect origin systems during sudden viral playback spikes?

## Source Set 13-18 Drills (12 Cards)

### Card 118
Front: Which invariants must hold for online auction highest-bid correctness?

### Card 119
Front: What escalation ladder would you use for auction bid contention?

### Card 120
Front: How do you design replay-safe live comment reconnect behavior?

### Card 121
Front: When do you choose SSE vs WebSocket for one-way comment fanout?

### Card 122
Front: How do you keep social post search fresh without synchronous indexing?

### Card 123
Front: Which mapping mistakes create long-term search reindex risk?

### Card 124
Front: What ingestion protections are needed for large price tracking crawlers?

### Card 125
Front: Which workflow checkpoints matter in price-drop alert orchestration?

### Card 126
Front: How do you avoid media payload bloat in Instagram-like feeds?

### Card 127
Front: What hybrid fanout strategy handles creator skew safely?

### Card 128
Front: How do you serve Top-K windows without query-time full scans?

### Card 129
Front: What late-event policy should be explicit in Top-K ranking APIs?

---

## AI Coding Interview Execution (12 Cards)

### Card 130
Front: What is the best first move before sending the first AI prompt in an interview?

### Card 131
Front: How do you show explicit ownership of architecture decisions while using AI?

### Card 132
Front: Which verify loop should run after each AI-generated code chunk?

### Card 133
Front: How should strategy differ between structured platform and open-ended BYOE rounds?

### Card 134
Front: What are the highest-value orientation checkpoints in a multi-file starter codebase?

### Card 135
Front: What interviewer signal indicates you are relying on AI too passively?

### Card 136
Front: How do you recover when AI suggests a design that conflicts with existing interfaces?

### Card 137
Front: Why is prompt-by-phase execution safer than one-shot full-solution prompting?

### Card 138
Front: What should you narrate before and after each prompt-response cycle?

### Card 139
Front: Which anti-pattern causes the most avoidable regressions in AI-enabled coding rounds?

### Card 140
Front: How do you choose what to skip under time pressure without compromising correctness?

### Card 141
Front: Which quality metrics best track progress in AI-assisted coding practice?

---

## Moderation and Abuse Defense (6 Cards)

### Card 142
Front: Why should content moderation separate inference, calibration, and enforcement instead of using one binary classifier output?

### Card 143
Front: Which guardrail metrics determine whether auto-remove thresholds are safe in production?

### Card 144
Front: What rollout pattern minimizes risk when tightening harmful-content policy?

### Card 145
Front: In bot detection, why is supervised-only detection insufficient for long-term resilience?

### Card 146
Front: What does a confidence-aware remediation ladder achieve versus immediate suspension?

### Card 147
Front: Which signals indicate coordinated bot campaigns are saturating investigator workflows?

---

## Recommendation Ranking Trade-offs (3 Cards)

### Card 148
Front: Why is a multi-stage recommendation pipeline (candidate -> light ranker -> heavy ranker -> reranker) preferred in low-latency feeds?

### Card 149
Front: How do you explain explore/exploit policy so it improves learning without harming core UX metrics?

### Card 150
Front: Which fairness and exposure metrics should be monitored when engagement-heavy labels bias recommendation outcomes?
