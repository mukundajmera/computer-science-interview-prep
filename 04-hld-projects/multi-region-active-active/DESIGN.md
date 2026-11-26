# Multi-Region Active-Active — Design

## 1. Requirements and Constraints

### Functional
- Route traffic geographically (US, EU, APAC).
- Asynchronous multi-master data replication.
- Conflict resolution using Hybrid Logical Clocks (HLC) and Last-Write-Wins (LWW).
- Automated regional failover.
- Read-after-write consistency for individual users.

### Non-functional
| Requirement | Target |
|---|---|
| Availability | 99.999% |
| Read latency | p99 < 50ms |
| Write latency | p99 < 150ms |
| Cross-region replication | < 1s under normal load |

## 2. Back-of-envelope estimation

Assume 100K requests/sec globally. *Note: All unsourced capacity, latency, and vendor-scale figures are illustrative scenario assumptions, not verified facts.*

| Metric | Value |
|---|---|
| Global traffic | 100K QPS total attempts (Reads: 80%, Writes: 20%, including failed/blocked operations) |
| Successful Write QPS per region | ~6.6K legitimate successful operations (assuming even distribution) |
| Replication overhead | 2x successful write traffic per region (receiving from 2 other regions) |
| Replication bandwidth | 6.6K * 2 * 2KB/record = ~26 MB/s cross-ocean links |
| Storage overhead | ~26 MB/s * 86400s = ~2.2 TB/day per region for replication logs |
| Tail-latency (p99) | < 50ms read, < 150ms write (assumed based on SSD limits and async replication) |

Decision impact: Cross-region bandwidth calculations represent theoretical roofline bounds derived from hardware specifications rather than measured guarantees. Bandwidth is well within standard dedicated link capacities, but replication queues must be durable to survive transient network partitions.

*Disclaimer: The APIs, consistency/availability contracts, failure/recovery traces, and alternative architectures detailed in this document are purely illustrative scenarios for design discussion. They do not represent a real deployed service.*

## 3. APIs

```http
POST /api/v1/records
Header: X-Client-Version: <version_token>
Body: { ... }

GET /api/v1/records/{id}
Header: X-Client-Version: <version_token>
Response Header: X-Server-Version: <version_token>

POST /api/v1/internal/replicate
Body: { "region": "US", "mutations": [...] }
```

## 4. Data model

- `UserRecord(id, data, hlc_timestamp, origin_region, tombstone)`
- `ReplicationCheckpoint(target_region, last_hlc_synced)`

Storage notes:
- Use a distributed key-value store optimized for wide-column or LSM tree structures (like Cassandra or ScyllaDB) which natively supports tunable consistency and timestamps.
- Include the `hlc_timestamp` on every row to allow deterministic Last-Write-Wins conflict resolution across regions without requiring centralized coordination.

## 5. High-level architecture

Mermaid source: [architecture.mmd](./diagrams/architecture.mmd).

1. **Global Traffic Management:** Uses Anycast BGP for fast, IP-level routing. If a region goes completely offline, BGP routes are automatically withdrawn, and traffic spills over to the next closest region.
2. **API Gateway & Routing:** Validates client version tokens. If a client was recently pinned to US but is routed to EU, the EU gateway can wait for replication to catch up or proxy the read to US.
3. **Multi-Master Database:** Accepts writes locally for low latency.
4. **Replication Engine:** Tails the database mutation log (CDC - Change Data Capture). Packages mutations into batches and pushes them to peer regions over dedicated redundant links.

## 6. Deep dives

### Conflict Resolution with Hybrid Logical Clocks
Physical clocks drift. Logical clocks (Lamport) lack real-world time relevance. The architecture uses Hybrid Logical Clocks (HLC) which combine physical time (NTP) with a logical counter. This guarantees that cause-and-effect relationships are preserved while providing a highly granular timestamp for LWW resolution.

### Read-After-Write Consistency
If a user updates their profile in the EU, and immediately refreshes, they must see the update.
- **Approach:** On write, the server returns a `version_token` (the HLC of the write).
- On subsequent reads, the client sends this token.
- If the handling region's data is older than the token (e.g., due to failover or replication lag), it blocks briefly, proxies the request, or forces a read repair.

### Failure and recovery paths
- **State Ownership and Exactly-Once End-to-End Guarantees:** The CDC / Replication Engine explicitly owns the replication state (the log of mutations). During a timeout or replay event (e.g., a replication push failure), the CDC engine uses named source offsets and checkpoints, combined with a transactional or idempotent sink boundary at the receiving multi-master database, to retry the batch. This strictly guarantees exactly-once end-to-end processing externally, ensuring updates are neither duplicated nor lost.
- **Network Partition (Split-Brain):** If the US region is severed from EU/APAC, it continues accepting local writes. Replication queues build up durably. Upon recovery, background anti-entropy scanners exchange Merkle trees (or similar structures) to reconcile missed updates, utilizing the HLC timestamps to merge safely.
- **Replication Link Degradation:** If cross-region latency spikes, local writes remain unaffected due to asynchronous replication. Dashboards alert on rising replication lag.

## 7. Trade-offs

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Routing | Anycast BGP | GeoDNS | Faster automated failover, no DNS caching issues. |
| Replication | Async Multi-Master | Sync Spanner-style | Prioritizes sub-150ms write latency over strict linearizability. |
| Conflict | LWW with HLC | CRDTs | Simpler generic data model; CRDTs are complex for nested objects. |

## Requirement-to-Section Review

- **Global Routing:** Handled in Section 5 (Global Traffic Management via Anycast BGP).
- **Data Replication:** Handled in Section 5 (Replication Engine / CDC) and Section 6 (Exactly-Once End-to-End Guarantees).
- **Conflict Resolution:** Handled in Section 6 (Conflict Resolution with Hybrid Logical Clocks).
- **Read-After-Write Consistency:** Handled in Section 6 (Read-After-Write Consistency using version tokens).
- **Partition Recovery:** Handled in Section 6 (Failure and recovery paths: Network Partition).
- **Availability, Latency, and Replication Lag Requirements:** Detailed as targets in Section 1 and supported by local-write architectures discussed in Section 5 and Section 7.

---
**Real-world reference**: See how Google Spanner solved this in the [Google Spanner case study](../../case-studies/google-spanner-truetime/)
