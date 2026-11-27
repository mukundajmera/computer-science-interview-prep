# Multi-Region Active-Active Replication — Interview Q&A

See [Theory](./THEORY.md) for the full architecture breakdown, conflict strategies, and decision table.

## Q1: When is multi-region active-active actually worth the complexity over active-passive?

**Model Answer:** Choose active-active only when you need both low-latency writes for globally distributed users and sub-minute RTO across a full regional outage. Active-passive (single primary region with warm standby and local read replicas) is far simpler because a single writer eliminates write conflicts. If most writes come from one geography or your SLA tolerates a 5–15 minute failover, active-passive gives you disaster recovery without conflict resolution, split-brain reconciliation, or double-write egress costs.

**Follow-up:** What happens if you run active-passive for two years and never test a real failover?
*Strong signal:* Standby drift—untested failover paths accumulate missing capacity, stale firewall rules, or unapplied schema/config changes, turning a planned 5-minute RTO into hours during a real outage.

## Q2: How do GeoDNS and Anycast differ for multi-region traffic routing, and where does each fall short?

**Model Answer:** GeoDNS returns different regional IP addresses based on the resolver's location or measured latency. Its weakness is caching: recursive DNS resolvers honor TTLs (30–60 seconds) and sometimes cache longer, so traffic keeps hitting a dead region until caches expire. Anycast advertises one IP prefix from multiple edge locations via BGP, shifting traffic in seconds when a site withdraws routes. Its weakness is stateful TCP sensitivity—mid-flight BGP route changes can send packets to a different edge and reset connections unless edge proxies terminate TLS and tunnel cleanly to backends.

**Follow-up:** How would you combine both in a real global architecture?
*Strong signal:* Terminate client connections at Anycast edge points of presence for fast TLS and instant edge failover, then route from edge to regional origins using health-aware origin routing or internal service meshes.

## Q3: Why is Last-Write-Wins (LWW) dangerous in multi-region active-active systems?

**Model Answer:** LWW picks the update with the highest timestamp and discards the other, which creates two failure modes. First, physical clocks across data centers drift even with NTP (typically milliseconds, and sometimes hundreds of milliseconds during slews or VM pauses), so an older write from a slightly fast clock can overwrite a newer write. Second, even with synchronized clocks, LWW causes silent data loss when two regions update different fields of the same record concurrently—one entire update is dropped.

**Follow-up:** Do Hybrid Logical Clocks (HLC) eliminate data loss in LWW?
*Strong signal:* No—HLCs preserve causal ordering (happens-before) without relying purely on wall clocks, but for genuinely concurrent writes they still break ties arbitrarily and drop the losing write.

## Q4: How do CRDTs solve write conflicts, and what are their practical limits?

**Model Answer:** Conflict-Free Replicated Data Types encode deterministic merge rules into the data structure itself so replicas always converge without coordination. State-based CRDTs merge full or delta states using a commutative, associative, and idempotent function (like an OR-Set for a shopping cart or a PN-Counter for likes); operation-based CRDTs broadcast commutative operations. Their limits are metadata overhead (per-replica vectors and tombstones for deletes) and expressiveness—CRDTs cannot enforce global invariants like preventing an account balance from dropping below zero.

**Follow-up:** How would you prevent tombstone metadata from growing unbounded in an OR-Set?
*Strong signal:* Track causally stable versions across all active replicas (version vectors) and periodically garbage-collect tombstones once every replica has observed the removal.

## Q5: What is a per-key home region, and why do many production systems prefer it over unrestricted multi-master writes?

**Model Answer:** A per-key home region assigns each user, tenant, or partition a single owning region that serializes writes for that key while replicating asynchronously to other regions for reads or disaster recovery. Because most users stay near their home region, they get local write latency with zero write conflicts. Traveling users incur one cross-region forward to their home region, or trigger a controlled ownership migration. It delivers 90% of active-active's latency and availability benefits without LWW data loss or CRDT modeling complexity.

**Follow-up:** What happens when a user's home region goes completely offline?
*Strong signal:* Decide upfront between CP (reject writes for those users until quorum/failover completes) and AP (temporarily promote a secondary region to accept writes, fencing the old home region and reconciling any unreplicated window on recovery).

## Q6: How do you guarantee read-your-writes when replication lags across regions?

**Model Answer:** Asynchronous cross-region replication typically lags 50–300 ms, so a read routed to a different region right after a write can return stale data. There are three practical defenses: sticky session routing (pinning the user to the writing region for a short window), causal consistency tokens (returning a write LSN or version watermark that the reading replica must reach before answering, or else forwarding the read to the writer), and reading directly from the home region for critical user-owned views.

**Follow-up:** What should the reading replica do if it never catches up to the client's watermark within a timeout?
*Strong signal:* Fail over the read to the writer region if reachable, or degrade gracefully with a stale-read indicator or error depending on whether the endpoint prioritizes freshness or availability.

## Q7: What causes split-brain in an active-active deployment, and how do you handle it safely?

**Model Answer:** Split-brain happens when a WAN partition isolates two active regions while both remain reachable to local users, causing their datasets to diverge independently. If the data model is AP (CRDTs or conflict-logged LWW), both sides stay writable and reconcile automatically once the link heals. If the workload requires single-writer semantics per key or partition, you prevent split-brain by requiring a cross-region quorum (odd number of regions or a lightweight witness in a third region) and attaching monotonic fencing tokens to reject writes from an isolated stale leader.

**Follow-up:** Why is a two-region cluster without a third-region witness unable to safely auto-failover?
*Strong signal:* Neither region can tell whether the other region crashed or the inter-region link failed; if both promote themselves, you get split-brain, and if neither promotes, you lose availability.

## Q8: How do you avoid cascading overload when an entire active region fails?

**Model Answer:** When one region in a 2-region active-active setup fails, the surviving region immediately receives 2x traffic while its caches are cold for the displaced users. To survive this, provision regional failover headroom (keep each region under ~40–50% peak utilization in a 2-region setup, or ~65% in a 3-region N+1 setup), use progressive traffic shifting and load shedding for low-priority endpoints, pre-warm or replicate critical cache keys, and run periodic regional evacuation game days to validate autoscaling speed.

**Follow-up:** Why does adding a third active region often reduce total idle compute cost compared to two regions?
*Strong signal:* Two regions require 100% spare capacity (50% utilization cap each), whereas three regions in an N+1 layout only need 50% spare capacity (up to ~66% utilization each) to absorb one full regional outage.

## Q9: How do data residency laws (such as GDPR) affect multi-region active-active design?

**Model Answer:** Residency regulations often prohibit replicating personal identifiable information (PII) outside a defined jurisdiction, which rules out naive global active-active replication of all tables. The standard pattern is cell-based regional pinning: store and replicate EU user PII strictly within EU regions (for example, two EU regions for active-active resilience within the bloc), and replicate only minimal, non-PII routing metadata globally so any edge location can direct a user to their compliant regional cell.

**Follow-up:** What breaks if your global logging or analytics pipeline still streams raw request payloads to a central US data lake?
*Strong signal:* Operational telemetry becomes a compliance leak; PII must be scrubbed or tokenized at the regional boundary, or analytics pipelines must run inside the same residency zone.

## Q10: Which workloads should avoid asynchronous active-active writes, and what should you use instead?

**Model Answer:** Workloads with strict global invariants—such as double-entry financial ledgers, seat/ticket reservations, or unique username allocation—should not use asynchronous multi-leader writes because concurrent regional writes can oversell or double-spend before replication converges. Instead, use per-key home regions (pinning each account or event to one authoritative region) or a multi-region consensus database (Paxos/Raft quorum across regions) that guarantees linearizability at the cost of cross-region write latency.

**Follow-up:** If you use a multi-region consensus database across US, EU, and Asia, how can you keep writes fast for regional users?
*Strong signal:* Place the Raft/Paxos leaseholder (leader) and a majority of voting replicas for each regional shard inside or near the user's home geography, while keeping an asynchronous or non-voting replica in distant regions for local stale reads.
