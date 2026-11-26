# 📋 HLD Design: Distributed Unique ID Generator (Snowflake)

> **Evidence Contract Note:** This document adheres to the `curriculum-evidence-contract.md`. 
> Target Layer: [Beginner / Core / Staff]
> HLD designs remain docs-only unless an explicit policy exception is noted. Unsourced figures are scenario assumptions, not verified external facts.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: Distributed Unique ID Generator (Snowflake variant).
- Core user value: Generate highly scalable, time-ordered, 64-bit numerical IDs for distributed systems.

### Functional Requirements
- [x] FR1: Generate globally unique 64-bit numerical IDs.
- [x] FR2: IDs must be strictly monotonic (sortable by time of generation).
- [x] FR3: Support a decentralized, collision-free generation process.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.999% (Highly Available) |
| Read latency | Not applicable (no read endpoint, only generation) |
| Write latency | < 2ms at P99 (Generation latency) |
| Throughput | > 10,000 IDs/sec/node |
| Consistency | Strong (Strictly collision-free) |
| Durability | Not applicable (stateless generation) |

### Constraints
- Must fit within 64 bits to map to `BIGINT` in SQL databases.
- Resilient against NTP backward clock shifts.
- Cannot rely on a centralized bottleneck during ID generation.

### Out of Scope (Non-Goals)
- Storing or associating IDs with application data.
- Global strict monotonicity (IDs are strictly monotonic within a worker, and roughly monotonic globally).

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| Active generator nodes | 1,024 nodes | scenario assumption |
| Target generation rate per node | 4,000 IDs/ms | scenario assumption |
| Peak global QPS | ~4,000,000,000 IDs/sec | 1000 nodes × 4000 IDs/ms × 1000 ms/sec (Theoretical max) |
| Peak Bandwidth | ~32 GB/sec | 4B IDs/sec × 8 bytes/ID (Outbound only, assuming raw 64-bit numbers without JSON overhead) |


### ID Format & Capacity

| Component | Bit Size | Capacity |
|---|---|---|
| Sign Bit | 1 bit | 0 (Always positive for numerical sorting) |
| Timestamp | 41 bits | $2^{41} \approx 2.19 \times 10^{12}$ ms $\approx 69$ years |
| Worker ID / Datacenter | 10 bits | $2^{10} = 1,024$ unique worker nodes |
| Sequence | 12 bits | $2^{12} = 4,096$ IDs per millisecond per worker |

### Decision Notes
- **41-bit timestamp:** Forces the use of a custom epoch (e.g., system launch date) to maximize the 69-year lifespan. Standard Unix epoch would exhaust too quickly.
- **10-bit Worker ID:** Limits the cluster size to 1,024 active nodes. This necessitates a robust lease and reclamation system (e.g., ZooKeeper ephemeral nodes).
- **12-bit sequence:** Caps generation at 4.096M IDs/sec/node. If traffic spikes beyond 4,096 IDs in a single millisecond, the thread must block until the next millisecond.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: gRPC (preferred for low latency internal microservices) or REST.
- Auth model: Internal service-to-service authentication (e.g., mTLS).
- Rate limiting policy: If the internal sequence hits 4,096 in a millisecond, subsequent calls block until the clock ticks to the next millisecond.

### Core Endpoints
```http
GET /api/v1/id
```
**Response:**
```json
{
  "id": "154389145601245184",
  "timestamp": "2023-10-25T14:32:01.123Z"
}
```
*(Note: IDs should be returned as strings in JSON to prevent precision loss in JavaScript clients, which only safely support 53-bit integers).*

### Error Model
- `503 Service Unavailable`: Thrown if the clock moves backward significantly and the node cannot generate a safe ID (`ClockMovedBackwardsException`).
- `500 Internal Server Error`: Zookeeper connection failure during initialization.

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- **WorkerNode**: Represents a single ID generator instance, requiring a unique 10-bit ID.

### Storage Choices
- Primary DB: **ZooKeeper** or **etcd**. (reason: Strong consistency for leasing worker IDs).
- Local State: **In-Memory variables** (reason: ID generation must be blazingly fast; no disk I/O on the critical path).

### State Variables (In-Memory per Node)
- `workerId`: Integer (0-1023).
- `lastTimestamp`: Long (tracks the last millisecond an ID was generated).
- `sequence`: Integer (0-4095).

---

## 5. 🏗️ High-Level Architecture

![Architecture](diagrams/architecture.mmd)

### Component List
- **ID Generator Application:** The stateless (except for local sequence/time) service generating the IDs.
- **ZooKeeper Cluster:** Manages the assignment and leases of the 10-bit Worker IDs.

### Generation Path
1. Client requests an ID from the Generator.
2. Generator fetches the current system time in milliseconds.
3. If time equals `lastTimestamp`, increment `sequence`.
   - If `sequence` > 4095, block until the next millisecond.
4. If time > `lastTimestamp`, reset `sequence` to 0.
5. Update `lastTimestamp` to current time.
6. Bitwise OR the components together: `(timestamp << 22) | (workerId << 12) | sequence`.
7. Return the 64-bit integer.

### Explicit Traces

#### Normal Trace
1. Node boots up, connects to ZooKeeper, and claims an available Worker ID (e.g., `Node-42`).
2. Node serves millions of requests using its local clock and sequence counter.

#### Failure Trace: NTP Clock Sync (Backward Shift)
- **Dependency timeout behavior:** If the clock moves backward, `current_time < lastTimestamp`.
- **Degraded mode / Recovery:**
  - **Wait Strategy:** If the drift is minor (< 5ms), the thread sleeps for the drift duration and retries.
  - **Fail Fast Strategy:** If the drift is large, the generator throws a `ClockMovedBackwardsException` and returns a 503, dropping the node from the load balancer until the clock catches up.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Worker ID Assignment and Recovery
- **Bottleneck:** We only have 1,024 Worker IDs. If nodes restart frequently, we could exhaust them.
- **Chosen pattern:** Use ZooKeeper **ephemeral sequential nodes**. When a worker boots, it creates a node like `/worker/id-00042`. It caches this ID locally.
- **Failure handling:** If the worker crashes, its ZooKeeper session expires, and the ephemeral node is deleted, freeing up the ID `42` for a new worker. 

### Deep Dive B: Clock Drift Handling
- **Bottleneck:** System clocks can drift and NTP daemon might shift the clock backwards to correct it. Generating an ID with a past timestamp will cause a duplicate if the sequence resets.
- **Chosen pattern:** Sleep-wait fallback. The system explicitly checks `if (currentTime < lastTimestamp)`.
- **Trade-off accepted:** By choosing to sleep or reject requests, we trade availability for strict consistency (collision prevention) during anomalous clock events.

---

## 7. 📈 Staff-Level Analysis (Optional)

- **Sequence Borrowing (Advanced Drift Mitigation):** Instead of failing fast on a backward clock shift, a system could "borrow" sequence numbers from the future by artificially advancing the timestamp, provided it hasn't exceeded the maximum sequence limit for the borrowed milliseconds. This keeps availability high during NTP syncs at the cost of slight logical time skew.
- **Dual-Language Parity:** Implementing this core algorithm requires careful attention to language specifics. For instance, Python handles arbitrarily large integers automatically, while Java requires `long` and careful unsigned/signed bit shifting (`>>>` vs `>>`).

---

## 8. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now |
|---|---|---|---|
| Algorithm | Snowflake (Time + Worker + Seq) | UUIDv7 | Fits strictly in 64 bits, standard DB indexing. |
| Worker Coordination | ZooKeeper | Static Config Files | Allows dynamic auto-scaling and node replacement without manual config changes. |
| Time Sync Error | Fail / Block | Use Logical Clocks | Strict collision avoidance is prioritized over 100% availability during rare NTP errors. |

---

## 9. 🔮 Follow-up Questions

1. **What happens in 69 years when the timestamp bits overflow?** The system will fail to generate new IDs (or generate negative/invalid IDs). A migration strategy to a new ID format or shifting the custom epoch would be required beforehand.
2. **How do you handle JavaScript clients?** JS uses double-precision floats for numbers, losing precision above $2^{53}-1$. The API must serialize the 64-bit ID as a `string` in JSON responses.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I skipped clarifying requirements (Addressed: strict 64-bit numerical limit).
- [x] I did not mention failure handling (Addressed: Clock drift and ZK partitions).
- [x] I did not articulate trade-offs explicitly (Addressed: Consistency vs Availability on clock drift).

---

## 11. ✅ Wrap-up Summary

We designed a Distributed Unique ID Generator based on the Snowflake algorithm, generating 64-bit integers composed of a 41-bit custom timestamp, a 10-bit dynamic worker ID managed by ZooKeeper, and a 12-bit local sequence. This design ensures highly scalable, localized ID generation at up to 4 million IDs per second globally, while maintaining strict collision resistance through careful handling of NTP backward clock shifts and sequence exhaustion limits.
