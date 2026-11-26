# Design: Distributed Partitioned Commit Log Broker

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: Distributed Partitioned Commit Log Broker (Kafka/Pulsar equivalent).
- Core user value: Decoupled, high-throughput, fault-tolerant pub/sub messaging.

### Functional Requirements
- [x] FR1: Producers can publish messages to topics.
- [x] FR2: Consumers can subscribe to topics and read messages sequentially per partition.
- [x] FR3: Data is durably persisted to disk and replicated.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% for reads and writes |
| Read latency | Millisecond pub-to-sub latency |
| Write latency | < 10ms p99 at broker |
| Throughput | 5M events/sec ingress |
| Consistency | Configurable per producer (e.g., all replicas ack) |
| Durability | No data loss after acknowledgment |

### Constraints
- Must handle broker crashes without data loss.
- Must support horizontally partitionable topics.

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| Ingress Rate | 5,000,000 msg/sec | Peak target |
| Read Fanout | 5x | 5 consumer groups per topic on average |
| Read Rate | 25,000,000 msg/sec | Ingress × 5 |

### Storage

| Data Type | Avg Size | Daily Volume | 7-Day Retention |
|---|---|---|---|
| Event | 1 KB | 432 TB | ~3 PB |

### Decision Notes
- **Storage:** 3 PB requires a horizontally scaled cluster. Disk density implies hundreds of broker nodes just for storage capacity.
- **Throughput:** Network bandwidth will be the primary bottleneck. We must use Zero-Copy and batching.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: Custom binary over TCP for efficiency, avoiding HTTP overhead.

### Core Endpoints / RPCs (Bounded Stages & Invariants)

#### `POST /ProduceRequest`
- **Bounded Stage:** Ingress handling and replication.
- **Observable Success Invariant:** Message batch is durably written to the leader. If `required_acks=-1` (all), all In-Sync Replicas (ISR) have appended the batch before returning success.
- **Observable Failure Invariant:** If the leader is not available, or not enough replicas are in sync (when min ISR is not met), an error is returned and the message is not committed.

```http
POST /ProduceRequest
{
  "topic": "user_clicks",
  "partition": 4,
  "required_acks": -1,
  "batch": [bytes]
}
```

#### `POST /FetchRequest`
- **Bounded Stage:** Egress reading and consumption.
- **Observable Success Invariant:** Messages are returned starting from `fetch_offset` up to the High Watermark (HW). No uncommitted messages are exposed.
- **Observable Failure Invariant:** If `fetch_offset` is out of bounds, an offset out of range error is returned.

```http
POST /FetchRequest
{
  "replica_id": -1,
  "max_wait_time": 500,
  "topics": [{"topic": "user_clicks", "partitions": [{"partition": 4, "fetch_offset": 10050}]}]
}
```

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- Message: The atomic unit of data, containing key, value, timestamp, and headers.
- Partition: An ordered, immutable sequence of messages.
- Topic: A logical category for partitions.

### Storage Choices
- Primary DB: Raw disk files (Log Segments).
- Index: Sparse memory-mapped offset index files.

### Key Access Patterns
1. Read path query: Sequential disk scan using OS page cache.
2. Write path mutation: Append-only disk write.

### Partition and Index Notes
- Retention is configured per topic (time-based or size-based).
- Sparse indices map logical offsets to physical file positions.

---

## 5. 🏗️ High-Level Architecture

### Component List
- **Brokers:** Nodes storing data and serving requests.
- **Metadata Controller:** Manages cluster state and leader elections.
- **Producers:** Clients pushing data.
- **Consumers:** Clients polling data.

### Read Path
1. Consumer sends FetchRequest.
2. Broker looks up offset via sparse index.
3. Broker streams data via `sendfile` (Zero-Copy).

### Write Path
1. Producer batches messages.
2. Broker appends to active segment.
3. Broker waits for replicas.

### Failure-aware Path
- Broker crash: Controller detects failure, promotes new leaders for affected partitions.
- Network partition: In-Sync Replicas (ISR) shrink; writes continue if min-ISR met.
- Consumer crash: Consumer group coordinator detects timeout, triggers rebalance.

---

## 6. 🔍 Deep Dives

### Deep Dive A: In-Sync Replicas (ISR) protocol
- Bottleneck: Synchronous replication limits throughput.
- Chosen pattern: Maintain a dynamic set of followers (ISR) that are fully caught up with the leader.
- The leader writes locally, waits for fetches from all ISR nodes, and then advances the High Watermark (HW). Consumers only read up to the HW.

### Deep Dive B: Page cache and Zero-Copy delivery
- Bottleneck: CPU overhead copying data from disk to socket.
- Chosen pattern: Rely on OS page cache for recent data. Use `sendfile` system call to transfer data directly from page cache to NIC buffer.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Consumer tracking | Consumer Coordinator | Broker tracks | Decouples broker from consumer speed | Always |
| Replication | ISR | Quorum (Raft) | Better latency/throughput balance for logs | Rarely |

---

## 8. 🏫 Educational Simulation Model Boundaries

This design specifies a bounded educational simulation model.
- **No actual wire/disk durability/security**: This simulation does not implement actual Kafka/S3 wire protocols. It operates strictly in-memory or with simulated storage layers.
  - **Durability gaps**: Lacks actual `fsync` policies, OS page cache utilization, zero-copy `sendfile` semantics, and true physical disk segment persistence.
  - **Security gaps**: Lacks production-grade security mechanisms such as SASL/SSL authentication, encryption in transit/at rest, and ACL-based authorization.
- **Injected failures and environments**: All transports, clocks, storage layers, and failure scenarios (like network partitions or node crashes) are injected rather than relying on real OS or network anomalies.
- **Scope limitation**: It serves as a proof sketch for distributed patterns rather than a formally verified or production-ready implementation.
- **Every requested operation is assigned to a bounded stage and states observable success/failure invariants.**

---
**Real-world reference**: See how LinkedIn solved this in the [LinkedIn case study](../../case-studies/linkedin-feed/)
