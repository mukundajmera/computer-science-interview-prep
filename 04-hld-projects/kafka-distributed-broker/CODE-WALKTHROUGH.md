# Code Walkthrough: Distributed Partitioned Commit Log Broker

This document outlines the bounded educational simulation model for the Kafka-like Distributed Broker project. 

## Simulation Boundaries and Scope

This model is strictly an **educational simulation** of the distributed commit log system.
*   **No actual Kafka/S3 wire compatibility**: There is no implementation of the Kafka wire protocol or S3 API.
*   **No actual disk durability**: Data is not actually persisted to disk. Disk behavior is simulated using injected storage. This lacks true physical disk segment persistence, `fsync` flushing guarantees, OS page cache, and zero-copy semantics.
*   **No actual security**: Production-grade security mechanisms are not modeled. This lacks SASL/SSL authentication, encryption, and ACL-based authorization.
*   **Injected Dependencies**: The simulation relies on injected transports, clocks, storage, and failure points to observe and assert distributed system behaviors.
*   **Bounded Stage & Invariants**: Every requested operation is assigned to a bounded stage and states observable success/failure invariants.

## Component Contracts

The simulation covers three primary components, implemented in both Java (11+) and Python (3.8+).

### 1. `PartitionLog`

**Responsibility:** Manages append-only segment storage, sparse offset indexing (offset -> physical byte offset binary search), and rolling segments.

**Exact API Contract:**
*   `append(message: bytes) -> int`: Appends a message and returns its assigned offset.
*   `read(offset: int, max_bytes: int) -> list[bytes]`: Retrieves messages starting from the given offset.
*   `roll_segment(force: bool = False) -> None`: Rolls the active segment into an immutable segment.

**Bounded Stages & Invariants:**
*   **`append` (Bounded Stage: Active Segment Write):**
    *   *Observable Success Invariant*: Message is durably appended to the active segment, returning a monotonically increasing logical offset.
    *   *Observable Failure Invariant*: Simulates an exception if storage capacity is exhausted.
*   **`read` (Bounded Stage: Segment Read):**
    *   *Observable Success Invariant*: Returns a sequence of messages from the requested offset.
    *   *Observable Failure Invariant*: Returns an Offset Out of Range error if the requested offset is outside the retained range.
*   **`roll_segment` (Bounded Stage: Segment Rotation):**
    *   *Observable Success Invariant*: The current active segment becomes immutable, and a new empty active segment is created.
    *   *Observable Failure Invariant*: Fails with an exception if injected disk operations fail.

### 2. `BrokerCluster`

**Responsibility:** Handles In-Sync Replicas (ISR) tracking, High Watermark (HW) progression, Log End Offset (LEO) sync, leader election, and acknowledgment policies (`acks=0`, `acks=1`, `acks=all`).

**Exact API Contract:**
*   `produce(topic: str, partition: int, message: bytes, acks: str) -> None`: Submits a message to a leader broker.
*   `fetch(topic: str, partition: int, offset: int, replica_id: int) -> list[bytes]`: Fetches data up to the High Watermark (for consumers) or up to LEO (for followers).
*   `elect_leader(topic: str, partition: int) -> int`: Elects a new leader for the partition from the ISR list.

**Bounded Stages & Invariants:**
*   **`produce` (Bounded Stage: Leader Append & Replicate):**
    *   *Observable Success Invariant*: Message is written to the leader. If `acks=all`, the leader waits until all ISR followers have appended the message and advanced the HW before confirming.
    *   *Observable Failure Invariant*: Request is rejected if the leader is unreachable or the partition is missing.
*   **`fetch` (Bounded Stage: Follower/Consumer Read):**
    *   *Observable Success Invariant*: Returns data up to the High Watermark (HW) for standard consumers, or up to the Log End Offset (LEO) for ISR followers.
    *   *Observable Failure Invariant*: Returns an error if the topic or partition doesn't exist.
*   **`elect_leader` (Bounded Stage: Failure Recovery):**
    *   *Observable Success Invariant*: A new leader is chosen from the ISR list without data loss, and cluster metadata is updated.
    *   *Observable Failure Invariant*: Election fails if no ISR nodes are alive.

### 3. `ConsumerGroupCoordinator`

**Responsibility:** Manages partition assignment, heartbeat tracking, and the rebalance protocol.

**Exact API Contract:**
*   `join_group(group_id: str, member_id: str) -> None`: Registers a consumer with the group coordinator.
*   `heartbeat(group_id: str, member_id: str) -> None`: Renews the lease for a consumer.
*   `sync_group(group_id: str, member_id: str) -> dict[str, list[int]]`: Returns the assigned topic partitions to the member.

**Bounded Stages & Invariants:**
*   **`join_group` (Bounded Stage: Group Membership):**
    *   *Observable Success Invariant*: Consumer member is registered successfully with the group coordinator.
    *   *Observable Failure Invariant*: Rejects join request if the consumer group is marked as dead.
*   **`heartbeat` (Bounded Stage: Liveness Tracking):**
    *   *Observable Success Invariant*: Consumer's liveness lease is renewed successfully.
    *   *Observable Failure Invariant*: Rejects heartbeat and triggers a rebalance if the member is unknown or the timeout has elapsed.
*   **`sync_group` (Bounded Stage: Partition Assignment):**
    *   *Observable Success Invariant*: Returns a non-overlapping assigned topic partition list to the member.
    *   *Observable Failure Invariant*: Fails or times out if the group fails to stabilize.
