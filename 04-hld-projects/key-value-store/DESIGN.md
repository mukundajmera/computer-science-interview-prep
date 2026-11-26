# High-Level Design: Key-Value Store

## Data Partitioning and Replication

We use a consistent hash ring with virtual nodes to map keys to nodes.

```mermaid
graph TD
    Client -->|get(key) / put(key, value)| CoordinatorNode
    CoordinatorNode -->|hash(key)| HashRing
    HashRing --> Replica1
    HashRing --> Replica2
    HashRing --> Replica3
```

## Write Path

1.  Client sends `put(k, v)` to a Coordinator Node.
2.  Coordinator determines the `N` replicas for `k` using the Hash Ring.
3.  Coordinator generates a new Vector Clock.
4.  Coordinator sends the write to the `N` replicas.
5.  If at least `W` replicas acknowledge the write, it succeeds. If a node is down, the coordinator may use Hinted Handoff.

```mermaid
sequenceDiagram
    participant Client
    participant Coordinator
    participant Node1
    participant Node2
    participant Node3

    Client->>Coordinator: put(k, v)
    Coordinator->>Node1: write(k, v, VC)
    Coordinator->>Node2: write(k, v, VC)
    Coordinator-XNode3: write(k, v, VC) (Fails)
    Note over Coordinator: Node 3 is down
    Coordinator->>Node4 (Fallback): write hint(Node3, k, v)
    Node1-->>Coordinator: ack
    Node2-->>Coordinator: ack
    Coordinator-->>Client: Success (W=2 met)
```

## Read Path and Conflict Resolution

1.  Client sends `get(k)` to Coordinator.
2.  Coordinator requests `k` from all `N` replicas.
3.  Coordinator waits for `R` responses.
4.  If versions conflict (based on Vector Clocks), the coordinator returns all conflicting versions to the client for resolution, or applies a default policy (e.g., LWW). Read Repair is performed to update stale nodes.

```mermaid
sequenceDiagram
    participant Client
    participant Coordinator
    participant Node1
    participant Node2

    Client->>Coordinator: get(k)
    Coordinator->>Node1: read(k)
    Coordinator->>Node2: read(k)
    Node1-->>Coordinator: (v1, VC=[N1:1])
    Node2-->>Coordinator: (v2, VC=[N1:1, N2:1])
    Note over Coordinator: Conflict resolution (v2 > v1)
    Coordinator-->>Node1: Read Repair (v2, VC)
    Coordinator-->>Client: (v2, VC)
```
