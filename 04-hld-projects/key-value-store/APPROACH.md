# Approach: Dynamo-Style Key-Value Store

We adopt a Dynamo-style architecture to achieve high availability and incremental scalability.

## Core Abstractions

1.  **Data Partitioning (Consistent Hashing):** Keys are distributed across nodes using a replicated hash ring with virtual nodes (vnodes). This ensures uniform load distribution and minimizes data movement when nodes join or leave.
2.  **Replication (N/R/W Quorum):** Data is replicated to `N` distinct nodes. Reads require `R` successful responses, and writes require `W` successful responses. Setting `R + W > N` provides strong consistency, while `R + W <= N` allows for eventual consistency.
3.  **Conflict Resolution (Vector Clocks):** Due to eventual consistency, divergent versions of data may exist. We use vector clocks to capture causality and identify conflicts. Conflicts are resolved at read time, either automatically (e.g., last-write-wins) or by the client.
4.  **Temporary Failures (Hinted Handoff):** If a replica is temporarily down during a write, a fallback node stores the data locally as a "hint". When the replica recovers, the hint is sent to it, ensuring the intended replica eventually receives the data.
5.  **Permanent Failures (Anti-Entropy with Merkle Trees):** Nodes periodically synchronize their replicas in the background (anti-entropy) to detect and repair inconsistencies caused by missed updates or permanent node failures. Merkle trees are used to minimize the amount of data transferred during synchronization.
6.  **Membership and Failure Detection (Gossip):** Nodes use a gossip protocol to discover peer nodes, maintain the hash ring view, and detect node failures.
7.  **Storage Engine (LSM Tree):** Each node uses a Log-Structured Merge (LSM) tree for local storage, providing high write throughput via sequential appends and a Write-Ahead Log (WAL) for durability. Read repair can update stale replicas during a read operation.
