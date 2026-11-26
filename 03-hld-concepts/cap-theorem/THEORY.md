# CAP Theorem

CAP theorem frames trade-offs in distributed systems under network partition. It is a fundamental principle that governs how systems behave when communication between nodes fails.

## What is it?

In the presence of a partition, a distributed system cannot simultaneously guarantee both:
- Strong consistency for every read (linearizability)
- Full availability for every request

Partition tolerance is non-optional in practical distributed systems. You cannot choose not to have network partitions, as they are an unavoidable reality of physics and networking equipment. Therefore, your system must choose how to respond to a partition: either by sacrificing availability (rejecting requests to remain consistent) or sacrificing consistency (serving potentially stale data to remain available).

## The CA Myth in Networked Distributed Systems

A common fallacy in system design interviews is treating "CA" (Consistency and Availability without Partition Tolerance) as a valid choice for a networked distributed database. This is physically impossible. 

The "CA Myth" arises from a misunderstanding of what a partition is. In any system distributed across a network, network partitions are an inevitable physical reality. Switch failures, fiber optic cuts, router misconfigurations, or severe packet drops will happen. 

Because you cannot prevent network partitions, you cannot build a "CA system" over a network. If a partition occurs and you haven't designed for partition tolerance, your system will either drop requests (losing availability) or serve divergent data (losing consistency). Therefore, the only true architectural decision under a partition is between CP (Consistency/Partition Tolerance) or AP (Availability/Partition Tolerance). 

A single-node relational database on a single machine can be considered "CA" because it doesn't experience network partitions internally. But once it is networked and replicated, it must make a choice between C and A when the network fails.

## Partition Definition vs Node Failures

It is critical to distinguish a network partition from a node crash.

**Node Crash (Failure):** A node stops executing. It is dead. Failover systems handle this under normal operations (e.g., electing a new leader). As long as a quorum of nodes remains alive and can communicate, the system continues functioning without violating CAP.

**Network Partition:** A communication failure between surviving nodes. The nodes are completely alive, healthy, and processing information, but they simply cannot communicate with each other. 

In a partition, Node A receives a write, but cannot send it to Node B. If a client queries Node B, Node B must decide: do I return my local, potentially stale data (Availability), or do I return an error because I cannot verify if my data is the latest (Consistency)?

## Formal Model and Operation-Scoped Decisions

CAP was originally formulated by Eric Brewer in 2000 as a conjecture, and formally proven by Seth Gilbert and Nancy Lynch in 2002. In its formal definition, the CAP theorem applies specifically to linearizable atomic read/write operations when a network partition separates non-failing nodes. The proven result states that the service cannot guarantee both availability to every request and linearizability during that partition.

Modern systems rarely choose one static CAP mode (CP or AP) for the entire product. Instead, they make operation-scoped decisions. You should avoid claiming a product is permanently CP or AP without defining the model and failure assumptions.

For example, a modern datastore might allow developers to specify consistency levels per query. A critical financial transaction might be executed as CP, while a social media feed read might be executed as AP.

## Why do we need it?

CAP clarifies failure behavior. Interviews are less about memorizing "CP vs AP" labels for specific database vendors, and more about making explicit, operation-level decisions based on business requirements. You must understand the impact of network partitions and design your application's behavior accordingly.

## Requirements and constraints

Before choosing behavior, define:
- Which operations are correctness-critical (e.g., billing, inventory)
- The business impact of stale reads on the user experience
- Error budget and latency Service Level Objectives (SLOs)
- Region and replication topology and network reliability
- Recovery, reconciliation expectations, and manual intervention limits

## Core definitions

- Consistency (CAP): every read reflects the latest successful write (linearizability).
- Availability: each non-failing node returns a non-error response.
- Partition tolerance: system continues despite broken links between nodes.

## Operation-scoped decision model

Do not choose one CAP mode for the entire product. Choose per operation.

Examples:
- Seat booking: prefer consistency over availability during conflicts. If the network partitions, users should get an error rather than double-booking a seat.
- Product detail page: prefer availability with bounded staleness. If the network partitions, showing a cached description from 5 minutes ago is better than showing an error page.
- Wallet transfer: consistency-first write path, availability-friendly read path with clear freshness contract.

## Consistency spectrum (practical)

| Model | Typical use | Cost profile |
|---|---|---|
| Strong consistency | Payments, inventory claims | Higher latency / reduced write availability under partitions |
| Read-your-writes | User profile/settings UX | Session affinity or metadata overhead |
| Causal consistency | Social interactions, messaging ordering | Metadata + ordering complexity |
| Eventual consistency | Feeds, analytics counters | Temporary divergence |

## Design patterns by choice

### Consistency-leaning patterns
- Quorum writes/reads (e.g., Paxos, Raft consensus)
- Leader-based write authority with synchronous replication
- Idempotent retries with strict conflict handling mechanisms

### Availability-leaning patterns
- Multi-region local reads with asynchronous replication
- Active-active topologies with conflict resolution
- Conflict resolution strategies (Last-Writer-Wins, domain merge rules, CRDT-inspired logic where appropriate)

## Failure-mode walkthrough

Partition between Region A and Region B:
1. Detect partition (health checks/heartbeat timeout fail).
2. Decide per endpoint:
   - Critical write: reject/defer if quorum unavailable. Return a 503 Service Unavailable.
   - Non-critical read: serve local data with staleness semantics. Add a header indicating data might be stale.
3. Reconcile after partition heals. Background processes merge divergent timelines or replay queued events.

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Repeats "pick two of three" without operation-level trade-off or formal understanding |
| 3 | Correctly separates strong-consistency and availability-sensitive paths and defines partitions correctly |
| 5 | Defines endpoint-specific policy, mitigation, recovery plan, and understands the formal linearizability limits |

## Common pitfalls

- Claiming "CA systems" exist over a wide-area network (the CA Myth).
- Treating CAP as a static, system-wide label for a database vendor (e.g., "Cassandra is always AP").
- Confusing ACID consistency (database integrity constraints) with CAP consistency (linearizability of reads).
- Saying "always AP" or "always CP" with no business context or justification.
- Having no reconciliation or freshness contract strategy after a partition heals.

## Follow-up questions

1. Which endpoints in our design can return stale data safely without financial impact?
2. What is your freshness contract (seconds/minutes) for eventually consistent reads?
3. How do you communicate degraded mode or stale data to clients in the UI?
4. What reconciliation rules run after a network partition heals to resolve conflicts?
5. Which SLOs decide CP vs AP behavior for each path in our service mesh?

## Variants and extensions

- Per-endpoint consistency policy configured in the API gateway or service mesh proxy.
- Region-aware read strategy with graceful fallback to remote regions before degrading.
- Progressive degradation: disable writes to non-critical domains first to preserve core system stability.
- Hybrid design: strong core ledger (CP) with eventually consistent materialized projections (AP).

## References

- Brewer, E. A. (2000). Towards robust distributed systems. (PODC).
- Gilbert, S., & Lynch, N. (2002). Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services. ACM SIGACT News, 33(2), 51-59.

## Related concepts

- [PACELC Theorem](../pacelc-theorem/)
- [CAP Theory Foundations](../../00-theory/system-design-fundamentals/cap-theorem.md)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [Pattern Selection](../pattern-selection/)

## Detailed CA Myth Examination

To further demystify the CA myth, consider a theoretical system deployed across three data centers. If a backhoe cuts the fiber line connecting Data Center C to A and B, a partition has occurred. Data Center C is still running. Data Centers A and B are still running. If a user connected to Data Center C attempts to write data, the system faces an unavoidable choice. If it accepts the write, Data Center C is now inconsistent with A and B (Availability chosen, Consistency sacrificed). If it rejects the write, Data Center C remains consistent with A and B, but the user receives an error (Consistency chosen, Availability sacrificed). 

There is no magical "CA" third option where the system accepts the write and instantaneously beams it across the severed fiber optic cable to maintain consistency. The laws of physics dictate that the system must choose CP or AP during the partition.

## Formal Verification and Limits

When discussing CAP in a formal context, it's important to recognize that formal verification often involves proving properties about algorithms under specific adversarial conditions (like asynchronous networks with unbounded delays). In these models, the impossibility of achieving both linearizability and availability in the presence of partitions is an absolute mathematical boundary, not just an engineering rule of thumb.

However, in practice, engineers work with probabilistic models and bounds. We might use terms like "highly available" or "strongly consistent under typical conditions," but we must always remember that the theoretical boundary established by Gilbert and Lynch remains. We design systems to mitigate the impact of partitions, but we can never build a networked system that guarantees both properties perfectly when the network fails.
