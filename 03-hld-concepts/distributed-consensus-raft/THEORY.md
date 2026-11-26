# Distributed Consensus: Raft Protocol and Multi-Paxos Deep Dive

Distributed consensus is the fundamental problem of getting multiple nodes in a distributed system to agree on a single state or value, even in the presence of network partitions and node failures. The two most prominent protocols for achieving this are Paxos (specifically Multi-Paxos) and Raft. While Paxos was historically the standard, Raft was explicitly designed to be more understandable while offering equivalent safety and performance.

## Leader Election State Machine

Raft simplifies consensus by relying on a strong leader. At any given time, every node in a Raft cluster is in one of three states:
- **Follower**: Passive nodes that only respond to requests from leaders and candidates. All nodes start in this state.
- **Candidate**: If a follower receives no communication from a leader over a specified period (the election timeout), it transitions to a candidate and initiates an election to become the new leader.
- **Leader**: The single active node that handles all client requests and replicates log entries to the followers.

### Randomized Election Timeouts

To prevent split votes where multiple followers become candidates simultaneously, Raft uses **randomized election timeouts**, typically ranging between 150ms and 300ms. The randomization ensures that usually, only one node times out and initiates an election, allowing it to win the election before other nodes time out.

### RequestVote RPC

When a candidate starts an election, it increments its current term and sends `RequestVote` RPCs to all other nodes. A node will grant its vote if:
1. The candidate's term is greater than or equal to the voter's current term.
2. The voter has not already voted for another candidate in this term.
3. The candidate's log is at least as up-to-date as the voter's log (checked via the index and term of the last log entry).

### The Pre-Vote Extension

A common issue in standard Raft is when a node becomes partitioned from the cluster. It will continually time out, increment its term, and start elections. Once the partition heals, this "zombie" node will have a very high term, forcing the current leader to step down, causing unnecessary cluster disruption.

The **Pre-Vote** extension solves this. A node will only increment its term and become a candidate if it first successfully completes a Pre-Vote phase, where it asks other nodes if they *would* vote for it. Since a partitioned node cannot reach a majority, it never enters the Pre-Vote phase successfully and never increments its term.

## Log Replication Invariants

Once a leader is elected, it begins servicing client requests. Each request is an instruction to be appended to the replicated state machine.

### AppendEntries RPC

The leader sends `AppendEntries` RPCs to replicate log entries to followers. This RPC is also used as a heartbeat (with no entries) to maintain leadership authority.

Key fields in `AppendEntries` include:
- `prevLogIndex` and `prevLogTerm`: Identifying the log entry immediately preceding the new ones.
- `entries[]`: The actual log entries being replicated.
- `leaderCommit`: The leader's `commitIndex`.

### Consistency Check

When a follower receives an `AppendEntries` RPC, it checks if its log contains an entry at `prevLogIndex` whose term matches `prevLogTerm`. 
- If they match, the follower accepts the new entries.
- If not, the follower rejects the RPC. The leader then decrements the `nextIndex` for that follower and retries, eventually finding the point where the logs match and overwriting any conflicting entries on the follower.

### Commit and Last Applied

- `commitIndex`: The index of the highest log entry known to be committed (safely replicated to a majority of nodes).
- `lastApplied`: The index of the highest log entry applied to the local state machine.
The protocol guarantees that once an entry is committed, it is durable and will eventually be executed by all state machines in the same order.

## Raft Safety Properties

Raft guarantees several crucial safety properties:

1. **Election Safety**: At most one leader can be elected in a given term.
2. **Leader Append-Only**: A leader never overwrites or deletes entries in its own log; it only appends new entries.
3. **Log Matching**: If two logs contain an entry with the same index and term, the logs are identical in all entries up through that index.
4. **Leader Completeness**: If a log entry is committed in a given term, then that entry will be present in the logs of the leaders for all higher-numbered terms.
5. **State Machine Safety**: If a server has applied a log entry at a given index to its state machine, no other server will ever apply a different log entry for the same index.

### Figure 8 Commit Invariant

A subtle edge case in Raft (often referred to as Figure 8 in the original paper) dictates that a leader cannot immediately determine that an entry from a *previous* term is committed by simply counting replicas. A leader can only safely commit entries from its *current* term by counting replicas. Once a current-term entry is committed, all preceding entries are implicitly committed due to the Log Matching property.

## Advanced Features

### Linearizable Read Problem in Raft

In distributed systems, a linearizable read ensures that once a write completes, any subsequent read must observe that write or a later one. In Raft, a naive approach to reads is for the leader to return the value currently in its state machine without consulting the cluster. However, this violates linearizability in the presence of network partitions.

If a leader is partitioned from the majority of the cluster, the majority may elect a new leader and commit new writes. The partitioned leader, unaware of its deposition, might still receive client read requests. If it serves these reads from its local state machine, it will return stale data, causing a split-brain scenario from the client's perspective.

The naive solution to guarantee linearizable reads is to treat every read request as a write: the leader appends a "read command" to the Raft log, replicates it to the majority, and waits for it to be committed before returning the result. While safe, this introduces significant latency, bloats the log, and adds substantial disk write overhead for purely read-only operations.

### ReadIndex Protocol

To achieve linearizable reads without the disk I/O and log bloat of the naive approach, Raft introduces the **ReadIndex Protocol**. This protocol requires zero disk writes while still guaranteeing linearizability:

1. **Step 1: Record `read_index`**: When the leader receives a read request, it records its current `commitIndex` as the `read_index`. This is the logical timestamp of the read.
2. **Step 2: Confirm Leadership**: The leader must prove it is still the authoritative leader (and not deposed by a partition). It does this by sending a round of empty heartbeat `AppendEntries` to the cluster. If it receives acknowledgments from a majority, it confirms its leadership.
3. **Step 3: Wait for Application**: The leader waits until its state machine's `lastApplied` index reaches or exceeds the `read_index`. This ensures the state machine has fully caught up to the state at the time the read was requested.
4. **Step 4: Execute Read**: The leader executes the read against its local state machine and returns the result to the client.

By verifying leadership and waiting for the state machine, the ReadIndex protocol ensures that the read observes all writes committed prior to the request, satisfying linearizability with only network overhead.

### LeaseRead Protocol (Leader Leases)

While ReadIndex eliminates disk I/O, it still requires a network roundtrip to a majority for every read to confirm leadership. To eliminate this network overhead, the **LeaseRead Protocol** uses leader leases based on physical clocks.

When a leader receives heartbeat acknowledgments from a majority, it establishes a time-based lease. The lease duration ($T_{lease}$) is set to be strictly less than the minimum election timeout ($T_{election}$) of any follower. During this lease period, followers guarantee they will not initiate a new election or vote for a new leader.

Therefore, as long as the leader's lease is valid, it can be absolutely certain it is still the sole leader. It can serve reads immediately from its local memory:

1. The leader checks if its current lease is valid.
2. If valid, it waits for its state machine to apply up to its current `commitIndex` (similar to ReadIndex Step 3).
3. It executes the read and returns the result, with ZERO network roundtrips to followers.

**Trade-off**: LeaseRead relies critically on bounded physical clock drift. If a leader's clock runs significantly slower than the followers' clocks (clock skew), the leader might falsely believe its lease is valid while followers have already elected a new leader. This would lead to stale reads and break linearizability.

### Follower Reads

To scale read throughput beyond the capacity of a single leader, read requests can be offloaded to followers. However, reading directly from a follower's local state machine could return stale data if the follower is lagging behind the leader.

To achieve linearizable **Follower Reads**, the follower must coordinate with the leader:

1. The client sends a read request to a follower.
2. The follower asks the leader for its current `commitIndex` (the leader typically uses ReadIndex or LeaseRead to ensure this value is safe and up-to-date).
3. The follower receives the `read_index` from the leader.
4. The follower waits until its own local state machine's `lastApplied` index reaches or exceeds the `read_index`.
5. The follower executes the read against its local state machine and returns the result to the client.

This approach distributes the read execution across the cluster while maintaining strong consistency guarantees.

### Dynamic Membership Changes & Joint Consensus

Changing the cluster membership (e.g., adding or removing nodes, scaling from 3 to 5 nodes) safely is complex. If nodes transition directly from the old configuration ($C_{old}$) to the new one ($C_{new}$), there is a risk of a disjoint majority: a subset of the cluster might form a majority under $C_{old}$ and elect a leader, while another subset forms a majority under $C_{new}$ and elects a different leader, violating safety.

Raft addresses this using a two-phase **Joint Consensus** approach. The cluster transitions through an intermediate state where decisions require majorities from *both* the old and the new configurations.

1. The leader receives a request to change configuration to $C_{new}$.
2. The leader appends a special configuration log entry for Joint Consensus ($C_{old,new}$) and replicates it.
3. Once a node adds the $C_{old,new}$ entry to its log, it immediately begins using it for all future decisions. Under $C_{old,new}$, an election or commit requires a majority of $C_{old}$ **AND** a majority of $C_{new}$. This strictly prevents disjoint majorities.
4. Once the $C_{old,new}$ entry is committed (safely replicated to a joint majority), the cluster is safely in the transitional state.
5. The leader then appends the final $C_{new}$ configuration entry and replicates it.
6. Nodes immediately use $C_{new}$ upon appending it. Once $C_{new}$ is committed, the transition is complete, and nodes only in $C_{old}$ can be safely removed.

This protocol allows the cluster to continue serving client requests throughout the configuration change without pausing availability.

### Snapshot Compaction

Logs cannot grow indefinitely. Raft uses snapshotting for log compaction. Each server independently takes snapshots of its state machine, discarding the log entries up to that point. If a follower falls too far behind (its required entries have been discarded by the leader), the leader sends the snapshot using the `InstallSnapshot` RPC.


## Practical Considerations and Optimizations

While the base Raft protocol is simple and elegant, running it in production requires several optimizations and careful operational management to achieve high performance and reliability.

### Batching and Pipelining

To achieve high throughput, a production Raft implementation cannot afford to process requests one by one.

**Batching**: When a leader receives multiple client requests concurrently, it should batch them together into a single `AppendEntries` RPC. This significantly amortizes the network overhead and, more importantly, the disk synchronization (fsync) cost. Instead of issuing an fsync for every single log entry, the leader can write the entire batch and issue a single fsync.

**Pipelining**: In the standard protocol, a leader sends an `AppendEntries` RPC and waits for the follower to acknowledge it before sending the next one. This stop-and-wait approach limits throughput to the network latency. Pipelining allows the leader to send multiple `AppendEntries` RPCs to a follower in-flight simultaneously without waiting for acknowledgments. If a pipelined request fails or is rejected (due to a log mismatch), the leader must be careful to handle the rejection and potentially re-send the correct sequence of entries, but the optimistic case yields massive throughput gains.

### Asynchronous Disk Writes

Writing to stable storage (disk) is the primary bottleneck in Raft. An `AppendEntries` RPC is not considered successful by a follower until the entries are safely durably persisted to disk.

However, modern implementations often decouple the network response from the disk fsync. A follower might acknowledge the `AppendEntries` RPC as soon as the data is written to the operating system's page cache, without waiting for the slow fsync. While this technically violates the strict durability guarantee of the original paper (a power failure could lose the acknowledged entries), it is often an acceptable trade-off in highly available setups with many replicas across different failure domains, significantly reducing commit latency.

### Fast Election (Pre-Vote in Depth)

We mentioned Pre-Vote earlier as a mechanism to prevent partitioned nodes from disrupting the cluster. It also has implications for election speed.

When a leader fails, the cluster is temporarily unavailable until a new leader is elected. The speed of this election is critical for minimizing downtime.

In a standard election, a candidate increments its term and sends `RequestVote` RPCs. If it fails to get a majority (e.g., due to a split vote), it must wait for another randomized timeout before trying again.

The Pre-Vote phase acts as a filter. A node only enters a real election (and increments the term) if it successfully gathers pre-votes from a majority. This means that when a real election starts, the candidate is highly likely to win it immediately, reducing the chance of repeated split votes and accelerating the overall recovery time.

Furthermore, Pre-Vote ensures that a node with a lagging log cannot disrupt the cluster. It will fail to get pre-votes because its log is not up-to-date, preventing it from incrementing the term and forcing the current, up-to-date leader to step down.

### Handling Byzantine Failures

It's important to note that Raft is a Crash-Fault Tolerant (CFT) protocol. It assumes that nodes might crash, delay messages, or become partitioned, but it assumes they will not act maliciously or send corrupted data (Byzantine failures).

If a node in a Raft cluster becomes compromised and starts sending falsified `AppendEntries` or `RequestVote` messages, the safety of the protocol is completely compromised. Raft relies entirely on the honesty of the participating nodes.

For environments where malicious actors or extreme hardware corruption are a concern, Byzantine Fault Tolerant (BFT) protocols like PBFT (Practical Byzantine Fault Tolerance) or HotStuff are required. These protocols are significantly more complex and resource-intensive than Raft, requiring more communication rounds and cryptographic signatures to verify the authenticity of every message.


### Log Compaction Strategies in Production

While snapshotting is the standard mechanism for log compaction described in the Raft paper, production systems often employ more sophisticated techniques to minimize the performance impact of compaction.

**Incremental Compaction**: Taking a full snapshot of a very large state machine can be expensive, potentially blocking the main Raft thread and causing heartbeat timeouts (leading to false leader elections). Incremental compaction techniques involve creating the snapshot in the background, copying data continuously rather than halting the system.

**Log-Structured Merge-trees (LSMs)**: Many modern key-value stores built on Raft (like CockroachDB or TiKV) use LSM-trees (e.g., RocksDB) for their underlying state machine storage. The natural compaction process of an LSM-tree can be integrated with Raft's log compaction. The system can incrementally discard Raft log entries that correspond to data already flushed and compacted in the underlying LSM-tree.

**Snapshot Transfer Efficiency**: When a leader needs to send an `InstallSnapshot` RPC to a follower that is far behind, sending a multi-gigabyte snapshot over the network can be disruptive. Optimizations include chunking the snapshot, compressing the chunks, and limiting the bandwidth used for snapshot transfers to avoid starving regular Raft traffic.

### Observability and Debugging

Running Raft at scale requires deep observability. Operators need metrics and logs to diagnose issues like slow elections, frequent leadership changes, or degraded performance.

Key metrics to monitor in a Raft cluster include:
- **Leader Changes**: Frequent leadership changes often indicate network instability, aggressive election timeouts, or resource exhaustion on the leader node.
- **Commit Latency**: The time it takes for a proposed log entry to be committed. High commit latency usually points to slow disk I/O on the followers or network congestion.
- **Log Index Lag**: The difference between the leader's `commitIndex` and each follower's `lastApplied` index. A growing lag indicates a follower is struggling to keep up with the leader's write throughput.
- **Term Number**: Rapidly increasing term numbers suggest a cluster struggling to maintain a stable leader, potentially due to a partitioned node repeatedly timing out.

Detailed structured logging of state transitions, rejected RPCs, and disk sync durations is essential for post-mortem analysis of cluster failures.

## Contrast with Multi-Paxos



While both solve distributed consensus, their approaches differ:

- **Leader Dependency**: Raft requires a strong, stable leader for progress. Multi-Paxos can theoretically allow multiple leaders (or "proposers") simultaneously, although practically it often relies on a distinguished leader for performance.
- **Log Structure**:
  - **Raft**: Enforces a strict, contiguous log sequence. Entries must be committed in order, and there are no "holes" in the log.
  - **Multi-Paxos**: Allows instances to be agreed upon out-of-order. This can create "holes" in the log that must be filled before the state machine can advance, but it can potentially offer higher concurrency for independent operations.
- **Understandability**: Raft separates consensus into distinct subproblems (leader election, log replication, safety) with fewer edge cases, making it significantly easier to implement and reason about correctly compared to the monolithic and complex nature of Multi-Paxos.
