# Design Approach for Distributed Unique ID Generator

A structured breakdown of the architectural choices, alternatives, and technical directions for the distributed unique ID generator.

---

## 1. Requirements Clarification and Technical Scope

The core technical challenge is generating 64-bit numerical IDs rapidly across a distributed cluster without introducing a single point of failure or high-latency coordination on the critical path.

**Key constraints driving the design:**
- **Sortability:** IDs need to be roughly time-ordered to preserve locality in database indexes (like B-trees).
- **Format Size:** Must fit inside 64 bits to be compatible with database `BIGINT` columns and minimize storage overhead.
- **Independence:** Generation must occur locally on the node without network calls, aside from initial setup or failover.

---

## 2. Alternatives Considered

Before selecting the Snowflake approach, several alternative designs were evaluated.

### Approach 1: Multi-Master Database Auto-Increment

- **How it works:** Use a relational database with an auto-increment column. In a multi-master setup, set the `auto_increment_increment` to the number of nodes (e.g., Node 1 generates 1, 3, 5; Node 2 generates 2, 4, 6).
- **Pros:**
  - Simple to implement.
  - Guarantees uniqueness.
- **Cons:**
  - **Scalability bottleneck:** Writing to a central DB limits throughput.
  - **Single point of failure:** If the database goes down, ID generation stops.
  - **Hard to scale:** Adding or removing database nodes requires reconfiguring the increment logic, which is risky and complex.

### Approach 2: UUIDv4 (Random)

- **How it works:** Generate a 128-bit random number.
- **Pros:**
  - Zero coordination.
  - Decentralized and scales infinitely.
- **Cons:**
  - **Size:** 128 bits is too large for the 64-bit constraint.
  - **Not time-ordered:** UUIDv4 is purely random, leading to index fragmentation and poor write performance in relational databases (B-trees).

### Approach 3: UUIDv7 (Time-ordered)

- **How it works:** A 128-bit identifier that embeds a timestamp, making it sortable by time.
- **Pros:**
  - Decentralized.
  - Solves the index fragmentation issue by being time-ordered.
- **Cons:**
  - **Size:** Still 128 bits, violating the strict 64-bit numerical format requirement.

---

## 3. Selected Approach: Twitter Snowflake Algorithm

We choose a custom implementation inspired by Twitter's Snowflake algorithm. This approach generates a 64-bit integer by composing a timestamp, a worker ID, and a local sequence number.

### Why Snowflake?
- **64-bit Size:** Perfectly fits in a `BIGINT` and allows efficient storage and indexing.
- **Time-Ordered:** The highest bits represent time, guaranteeing that IDs generated later are larger, preserving locality in B-tree indexes.
- **Decentralized Generation:** Nodes only need to acquire a unique Worker ID once (e.g., at startup via ZooKeeper). Subsequent ID generation requires zero network calls, offering sub-millisecond latency and high throughput.

### High-Level Blueprint

1. **ID Layout Definition:** Define a fixed 64-bit structure: 1 sign bit, 41 timestamp bits, 10 worker ID bits, and 12 sequence bits.
2. **Epoch Customization:** Select a custom epoch close to the system's launch date to maximize the 69-year lifespan of the 41-bit timestamp.
3. **Worker Registration:** Use an external coordination service (ZooKeeper/etcd) to assign and lease 10-bit Worker IDs to generator nodes dynamically.
4. **Local State Machine:** Implement a thread-safe local generator that tracks the current millisecond and increments the 12-bit sequence.
5. **Clock Drift Protection:** Build logic to handle edge cases where the system clock moves backwards (e.g., NTP adjustments) by pausing, borrowing from the sequence, or failing fast.

---

## 4. Key Technical Risks and Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| **Clock backward shifts** | Duplicate IDs or total failure | Detect negative time delta. If `< 5ms`, sleep and retry. If larger, throw `ClockMovedBackwardsException` or borrow from sequence. |
| **Sequence exhaustion** | Duplicate IDs within the same ms | If the 12-bit sequence reaches 4,096 in one millisecond, block until the next millisecond. |
| **Worker ID exhaustion** | Cannot scale past 1,024 nodes | Use ephemeral nodes in ZooKeeper to recycle worker IDs when nodes die. |
| **Network partition to ZK** | Node cannot start/re-lease ID | Cache the worker ID locally. The critical path (generation) continues to function even if ZK is unreachable. |

This foundation leads directly to the detailed architecture in `DESIGN.md`.
