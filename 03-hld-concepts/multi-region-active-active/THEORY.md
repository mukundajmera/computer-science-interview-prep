# Multi-Region Active-Active Replication

## 📚 Mental Model

Multi-region active-active runs independent read and write stacks across two or more geographic regions at the same time. Users connect to a nearby region for low-latency reads and writes, and another region absorbs traffic if a region fails. The core trade-off is physics versus coordination: accepting local writes avoids cross-ocean round trips (80–250 ms), so replication runs asynchronously and the system must handle stale reads, concurrent write conflicts, and split-brain partitions.

## 🎯 What Problem It Solves

- **Primary bottleneck or design pressure:** Single-region architectures suffer high round-trip latency for distant users and lose write availability during a regional outage.
- **What changes when the concept is introduced:** Writes and reads terminate locally in multiple regions, cutting p95 latency for global traffic and lowering recovery time objective (RTO) toward seconds.
- **When it is a bad fit:** Strongly consistent workloads with frequent global contention (double-entry ledgers, strict unique inventory decrements) or small teams without the budget for multi-region operations and failover drills.

## 🔍 Recognition Cues

- **Interview phrasing that triggers this concept:** "Global users in North America, Europe, and Asia," "sub-100 ms write latency worldwide," "survive a full region outage with near-zero RTO," or "strict EU data residency."
- **Metrics or symptoms that point here:** Cross-continent write p99 exceeding 200 ms, regional outage blast radius violating a 99.99% SLA, or regulatory mandates restricting where personal data may be stored.

## 🏗️ Core Mechanics

### Active-Passive vs Active-Active

| Dimension | Active-Passive (Warm Standby) | Active-Active (Multi-Region Writes) |
|---|---|---|
| Write path | Single primary region; remote users cross WAN | Every active region accepts writes locally |
| Read path | Primary or local read replicas (stale reads possible) | Local reads in each active region |
| Failover (RTO / RPO) | Minutes to promote standby; RPO = replication lag | Seconds via traffic shift; RPO = unreplicated local writes |
| Write conflicts | None (single writer) | Possible unless keys are pinned to one home region |
| Operational complexity | Moderate; failover paths often go untested | High; conflict handling, dual deployments, and egress cost |

### Data Placement and Traffic Routing

- **GeoDNS (latency- or geolocation-based DNS):** Resolves a domain to the closest healthy region's load balancer. DNS resolvers cache records for their TTL (typically 30–60 seconds), and some recursive resolvers ignore short TTLs, which delays failover convergence.
- **Anycast (BGP-based routing):** Advertises the same IP prefix from multiple edge locations so BGP routes packets to the topologically nearest point of presence. Anycast shines for stateless HTTP/edge termination and fast failover, but mid-connection BGP route flaps can break long-lived TCP sessions unless edge proxies maintain stable backend tunnels.
- **Request-to-data routing:** Edge routing alone is not enough; an application gateway often inspects a user or tenant ID to decide whether to serve locally or forward the request over a private backbone to the record's owning region.

### Write Conflict Strategies

#### Last-Write-Wins (LWW) and Clock Problems

Each write carries a timestamp, and replicas keep the highest timestamp when concurrent updates collide. LWW is simple to implement, but physical wall clocks drift even with NTP synchronization (typically 1–50 ms, and worse during clock slews, VM pauses, or leap-second adjustments). If Region A's clock runs ahead of Region B's, Region A's older write silently overwrites Region B's newer write. Even with perfect clocks, LWW drops data whenever two regions update different fields of the same record concurrently. Hybrid Logical Clocks (HLC) combine physical time with a logical counter to preserve causality, yet they still discard one side of a true concurrent conflict.

#### Conflict-Free Replicated Data Types (CRDTs)

CRDTs embed deterministic, mathematically convergent merge rules into the data structure so replicas reach the same state regardless of message order or duplicates:
- **State-based (CvRDTs):** Replicas ship full or delta state and merge with a commutative, associative, and idempotent function (such as a Grow-Only Counter or Observed-Remove Set).
- **Operation-based (CmRDTs):** Replicas broadcast commutative operations (such as "increment by 1") over reliable, at-most-once delivery channels.

CRDTs prevent silent overwrites for counters, sets, collaborative text, and shopping carts, at the cost of extra metadata, tombstone growth on deletes, and limited applicability to invariants like non-negative account balances.

#### Per-Key Home Region (Regional Pinning)

Instead of allowing arbitrary concurrent writes to the same key everywhere, each user, tenant, or shard is assigned a single **home region** that owns authoritative writes for that key. Local users get fast writes without conflicts; roaming users either forward writes to their home region or trigger an explicit ownership transfer. When global strong consistency is required across regions, distributed consensus protocols (Paxos or Raft) commit writes across a cross-region quorum, trading write latency for linearizability.

### Replication Lag and Read-Your-Writes

Asynchronous cross-region replication typically lags by 50–300 ms under normal conditions and seconds during spikes. If a user writes in Region A and a subsequent read lands in Region B, they may see stale data. Common mitigations include:
- **Sticky routing:** Pin a user's session to one region for a short window after a write.
- **Causal tokens (version watermarks):** Return a monotonically increasing sequence number or LSN with each write; if the serving replica has not caught up to that watermark, it either waits briefly or forwards the read to the writer region.
- **Bounded staleness:** Allow local reads only when measured replication lag stays below a configured threshold.

### Failover and Split-Brain

When the WAN link between Region A and Region B breaks, both active regions still look healthy to local clients and keep accepting writes, creating a **split-brain** where data states diverge. Mitigation depends on the consistency contract:
- **AP data (LWW/CRDT):** Accept divergence during the partition and reconcile deterministically when connectivity returns, auditing conflict queues for anomalies.
- **CP or home-region data:** Use an odd number of regions (or an external witness in a third region) so only the quorum side continues accepting writes, and fence isolated regions with epoch tokens to prevent stale leaders from committing.
- **Graceful failover:** Drain unhealthy regions via multi-region health checks, verify downstream capacity before shifting 100% of traffic, and avoid automatic hair-trigger failovers that cause regional flapping.

### Data Residency and Compliance

Regulations such as GDPR or national data localization laws often require personal data to remain inside a specific geographic boundary. In a multi-region design, global active-active replication of raw PII violates residency rules. Teams solve this by partitioning user records into **regional cells** (for example, EU users pinned strictly to EU regions), keeping PII local, and replicating only non-PII routing indexes or anonymized aggregates globally.

### Cost and Operational Overhead

- **Failover headroom:** In a 2-region active-active setup, each region must run below ~40–50% peak utilization so it can absorb 100% of global traffic if the other region fails. With three regions (N+1), each region can run near 65%, lowering idle overhead.
- **Cross-region egress:** Replicating every write across regions multiplies network egress charges, especially for write-heavy workloads or large payloads.
- **Operational tax:** Multi-region deployments require automated canary rollouts per region, backward-compatible schema migrations, and regular chaos or failover game days.

## 📐 Concrete Example

Consider a global collaboration platform serving **200,000 reads/sec** and **40,000 writes/sec** split evenly between US-East and EU-West (80 ms WAN RTT):
- **Replication bandwidth:** At 2 KB average write payload, each region sends 20,000 writes/sec (about 40 MB/sec, or ~320 Mbps) across the WAN, totaling ~104 TB/month of cross-region egress per direction before compression.
- **Capacity headroom:** Each region handles 100k reads/sec and 20k writes/sec normally, but must be provisioned (or auto-scalable within seconds) for 200k reads/sec and 40k writes/sec during a full regional outage.
- **Hybrid data placement:** User profiles and documents use per-key home regions (pinned to US or EU for residency and conflict avoidance), presence counters use PN-Counter CRDTs, and session tokens replicate asynchronously with a 15-second sticky-routing cookie for read-your-writes.

## ⚖️ Trade-offs

| Strategy | Write Latency | Consistency | Conflict Risk | Use When | Avoid When |
|---|---|---|---|---|---|
| Active-Passive | High for remote users | Strong in primary | None | Single-region write locality; strict consistency | Global sub-100 ms write SLA or sub-minute RTO |
| Active-Active + Home Region | Low for local users | Strong per key | None (normal ops) | Most SaaS apps, user-scoped data, data residency | Heavy concurrent multi-region edits to one key |
| Active-Active + LWW | Low everywhere | Eventual | High (silent drops) | Idempotent state, caches, telemetry metadata | Collaborative edits or financial records |
| Active-Active + CRDT | Low everywhere | Strong eventual | Merged deterministically | Counters, sets, presence, shopping carts | Strict invariants (balance >= 0, unique slots) |
| Multi-Region Consensus | High (1+ WAN RTT) | Linearizable | None | Financial ledgers, global metadata, lock services | Latency-sensitive high-throughput user writes |

Illustrative systems span multiple ecosystems: Apache Cassandra, DynamoDB Global Tables, and Cosmos DB offer tunable or LWW multi-region replication; Redis Enterprise and Riak support CRDT data types; CockroachDB, YugabyteDB, and Google Spanner provide consensus-backed global consistency with per-row regional pinning.

## ⚠️ Failure Modes

- **Correctness:** Clock skew in LWW silently drops newer writes; missing read-your-writes watermarks cause users to see vanished edits right after saving.
- **Scale:** Shifting 100% of traffic from a failed region triggers a thundering herd and cold caches, knocking over the surviving region (cascading failure).
- **Operations:** Untested failover runbooks, asymmetric schema changes breaking replication consumers, or oscillating health checks causing route flapping.
- **Security/privacy:** Unfiltered async replication copying regulated EU personal data into a non-EU region, violating residency commitments.

## 📊 Observability

- **Metrics:** Cross-region replication lag (p50/p99 in ms and bytes), conflict rate per keyspace, per-region utilization versus failover headroom, and GeoDNS/Anycast health-check failure rates.
- **Logs/events:** Region drain/failover state transitions, rejected writes due to fencing epochs, and sampled conflict-resolution payloads for audit.
- **Alerts:** Replication lag exceeding RPO budget, any active region exceeding 50% capacity (2-region) or 65% (3-region), and sudden spikes in conflict or dead-letter replication queues.

## 💬 60-90 Second Answer

Multi-region active-active serves reads and writes from multiple regions simultaneously to cut global latency and survive full-region outages with near-zero RTO. The hard part is not routing—GeoDNS and Anycast handle traffic placement—it is data consistency across high-latency WAN links. Because synchronous cross-region writes add 80 to 250 ms per request, most active-active systems replicate asynchronously and choose a conflict model per workload: per-key home regions to avoid conflicts and satisfy data residency, CRDTs for mergeable types like counters and sets, or LWW only where silent overwrites are acceptable. To make it production-safe, I pair it with read-your-writes session tokens, N+1 regional capacity headroom, and regular failover drills.

## ❓ Follow-up Questions

1. How do you guarantee read-your-writes if a user's request fails over to another region 100 ms after a write?
2. Why does Last-Write-Wins still lose data even if NTP keeps clocks within 10 ms?
3. How do you design an active-active system when EU users must keep their PII strictly inside Europe?
4. See [Interview Q&A](./INTERVIEW-QA.md) for 10 full questions, model answers, and follow-ups.

## 📋 Rubric

| Strong Signal | Weak Signal |
|---|---|
| Matches conflict strategy (home region, CRDT, LWW, consensus) to specific data types instead of one-size-fits-all | Claims active-active is "strongly consistent and low latency everywhere" without addressing WAN RTT |
| Accounts for DNS TTL caching, replication lag, split-brain fencing, data residency, and N+1 failover headroom | Mentions GeoDNS and async replication but ignores failover overload, clock skew, or compliance boundaries |
| Quantifies replication bandwidth, latency budgets, and RPO/RTO trade-offs | Treats active-active as a default upgrade over active-passive without discussing cost or complexity |

## 🔗 Cross-links

- **Prerequisites:** [CAP Theorem](../cap-theorem/), [Database Replication](../database-replication/), [Data Partitioning](../data-partitioning/), [DNS](../dns/), [Load Balancing](../load-balancing/)
- **Related projects:** [Multi-Region Active-Active Architecture](../../04-hld-projects/multi-region-active-active/)
- **Case studies:** [Google Spanner and TrueTime](../../case-studies/google-spanner-truetime/)
- **Interview practice:** [Multi-Region Active-Active Interview Q&A](./INTERVIEW-QA.md), [Distributed Storage & Consensus Flashcards](../../flashcards/distributed-storage-consensus.md)
