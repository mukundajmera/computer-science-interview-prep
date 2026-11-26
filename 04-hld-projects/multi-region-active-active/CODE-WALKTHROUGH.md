# Multi-Region Active-Active Simulator Walkthrough

This bounded paired-language simulator (available in both Java and Python) models the core concepts of the Multi-Region Active-Active architecture described in the design documents. 

## 1. Simulator Mappings

- **API Gateway & Routing:** The entry point into the system is handled through the `RegionDatabase` instances (e.g., `us` or `eu`). Calling `.write()` or `.read()` simulates an external request being routed to a specific geographic region.
- **Multi-Master Database:** The internal state of each `RegionDatabase` acts as the local storage. Because multiple regions can be written to independently and simultaneously, this simulates a multi-master environment.
- **Conflict Resolution (LWW & HLC):** Every write assigns a `HybridLogicalClock` timestamp. The `applyReplication()` method explicitly checks this timestamp against existing records to enforce a deterministic Last-Write-Wins (LWW) conflict resolution policy. In the event of an exact time tie, it deterministically breaks ties using the origin region name (e.g., US > EU).
- **Replication Engine:** A dedicated `replicationQueues` data structure buffers writes destined for other regions. Calling `.replicateTo(peer)` explicitly triggers the background replication flush, mimicking an asynchronous replication push over the network.

## 2. Simplifications (In-Memory Simulator vs. Distributed System)

- **Transport:** We avoid heavy RPC frameworks, network retries, and actual network partitions by replacing inter-node communication with in-memory method calls and boolean flags (`isPartitioned`).
- **Clock:** True distributed clocks require NTP synchronization and handling of significant physical clock skew. The simulator safely assumes identical local machine time (`System.currentTimeMillis()` / `time.time()`) as the base physical component for the Hybrid Logical Clocks.
- **Security:** Client tokens, TLS, and authorization headers are entirely omitted.
- **Consistency:** Eventually consistent read-after-write is simulated instantly within the same `RegionDatabase`. Read-after-write across regions relies on manual execution of replication loops to reach an eventually consistent state.

## 3. Simulating the Network Partition (Split-Brain) Invariant

In our test suite (`testNetworkPartitionSplitBrain`), we explicitly simulate the exact failure scenario described in `DESIGN.md`.

1. **Partition:** We set `isPartitioned = true` on the `us` and `eu` regions, representing a severed ocean link.
2. **Concurrent Writes:** Both regions accept independent local writes to the same key (`shared-doc`) without attempting coordination.
3. **Queue Build-Up:** Writes are appended to local durable replication queues while the partition lasts. `replicateTo()` calls fail to transfer state.
4. **Healing & Anti-Entropy:** When the partition is healed (`isPartitioned = false`), we trigger replication in both directions.
5. **Conflict Resolution:** The nodes utilize their `HybridLogicalClock` timestamps to determine the latest update (the EU write, which happened later), successfully resolving the split-brain scenario. Both nodes converge on the exact same eventual state.
