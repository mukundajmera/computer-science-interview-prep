# Distributed Storage & Consensus Quiz

20 multiple-choice questions focusing on distributed storage, consensus, and architecture trade-offs.

Time: 30 minutes
Difficulty: Expert

---

## 🎯 Scoring Guide

| Score | Range | Assessment | Recommendation |
|-------|-------|------------|----------------|
| 18-20 | 90-100% | **Excellent** | Staff+ Level |
| 15-17 | 75-89% | **Good** | Senior Level |
| 12-14 | 60-74% | **Fair** | Mid Level |
| 0-11 | 0-59% | **Needs Work** | Rebuild fundamentals |

---

## Section 1: Consensus & Snapshots

### Question 1
In a 5-node Raft cluster, the leader (Node A) receives a write request for entry X and appends it to its local log. Node A then sends `AppendEntries` RPCs to the four followers. Nodes B and C receive the RPC, write to their logs, and acknowledge. Node D crashes before receiving the RPC, and Node E's network is partitioned. The leader then commits the entry and applies it to its state machine. Immediately after, Node A crashes. Node B's election timeout expires first, and it requests votes. Can Node B be elected leader, and what happens to entry X?

A) Node B cannot be elected because only Node A knew X was committed.
B) Node B cannot be elected because it does not have a majority.
C) Node B can be elected, but it will overwrite entry X with a no-op entry from its new term to establish leadership.
D) Node B can be elected; entry X is preserved because Node B contains it, and Raft's Leader Completeness Property ensures B's log is at least as up-to-date as a majority of the cluster.

### Question 2
During a Raft leader election, Node F receives a `RequestVote` RPC from Candidate G. Candidate G's last log index is 15 and last log term is 3. Node F's last log index is 12, but its last log term is 4. According to Raft's election restriction, how must Node F respond?

A) Node F grants the vote because G has a higher log index (15 > 12).
B) Node F denies the vote because F's last log term is higher (4 > 3), indicating F's log is more up-to-date.
C) Node F grants the vote but requires G to append missing entries from term 4.
D) Node F ignores the request until it times out itself.

### Question 3
The Chandy-Lamport algorithm is used to capture a consistent global state (snapshot) of a distributed system. If Process P1 initiates the snapshot by recording its local state and sending a marker message to Process P2, what must P2 do immediately upon receiving the marker *for the first time*?

A) Wait for all in-flight messages to arrive, then record its state.
B) Send its local state back to P1 without recording anything locally.
C) Record its local state, and start recording all incoming messages on other channels until it receives markers on them.
D) Halt all local processing until the global snapshot is complete.

### Question 4
In the Chandy-Lamport snapshot algorithm, how are messages that were "in transit" (sent before the sender recorded its state, but received after the receiver recorded its state) handled?

A) They are captured by the receiver, which records all messages arriving on a channel after recording its local state and before receiving the marker on that channel.
B) The algorithm assumes FIFO channels, meaning in-transit messages are impossible.
C) They are explicitly retransmitted by the sender after the snapshot.
D) They are discarded to maintain consistency.

## Section 2: Distributed Transactions

### Question 5
In a Two-Phase Commit (2PC) protocol, the coordinator sends a `PREPARE` message to all participants. Participant P1 replies `YES` (prepared), while Participant P2 crashes before replying. Before the coordinator can make a decision and send the `ABORT` or `COMMIT` message, the coordinator itself crashes. What state is P1 left in, and what is this problem called?

A) P1 automatically aborts after a timeout (Fail-Fast).
B) P1 is blocked indefinitely holding resource locks until the coordinator recovers or a new coordinator queries P2's state (Blocking Coordinator Failure).
C) P1 automatically commits to preserve data availability.
D) P1 queries P2 directly to resolve the transaction.

### Question 6
To mitigate the blocking problem of 2PC, a microservices architecture adopts an Orchestration-based Saga for a long-running distributed transaction spanning three services (A, B, C). Service A completes successfully. Service B completes successfully. Service C fails due to a permanent business constraint validation error. What action must the Orchestrator take?

A) Invokes application-level compensating transactions on Service B, then Service A, to explicitly reverse the committed changes.
B) Issues standard rollback commands (`ROLLBACK TRANSACTION`) to the databases of Service A and Service B.
C) Retries Service C infinitely using exponential backoff.
D) Aborts the saga and leaves the system in a partially consistent state.

### Question 7
When designing compensating transactions for a Saga, which property is strictly required to handle temporary network failures during the compensation phase?

A) Isolation (locking records to prevent concurrent reads).
B) Linearizability (strict ordering of all operations).
C) Atomicity (executing all compensations in a single database transaction).
D) Idempotency (the ability to safely retry the compensation multiple times).

## Section 3: Storage Engine Trade-offs

### Question 8
In an LSM-Tree (Log-Structured Merge-Tree) storage engine using Leveled Compaction (like RocksDB), what is the primary structural difference between Level 0 (L0) and Level 1 (L1)?

A) L0 files are immutable, while L1 files are mutable.
B) L0 is stored in RAM (MemTable), while L1 is stored on disk.
C) L0 SSTables may have overlapping key ranges, whereas SSTables within L1 (and deeper levels) have strictly non-overlapping key ranges.
D) L0 uses B-Trees, while L1 uses Hash Indexes.

### Question 9
Which type of amplification is typically the highest in a Leveled Compaction LSM-Tree when compared to a traditional B+Tree?

A) Read Amplification (number of disk reads per logical read).
B) Space Amplification (ratio of data size on disk to logical data size).
C) Network Amplification (bytes transferred over the network).
D) Write Amplification (ratio of bytes written to disk to bytes written by the application).

### Question 10
In PostgreSQL, Multi-Version Concurrency Control (MVCC) is implemented by storing multiple versions of a row in the main table pages. What critical background process is required to reclaim space from dead tuples, and what catastrophic failure mode does it prevent?

A) Autovacuum; prevents Transaction ID (XID) wraparound, which would cause old rows to suddenly appear as in the future and become invisible.
B) Checkpointer; prevents WAL log exhaustion.
C) Compactor; prevents Read Amplification from exceeding logarithmic bounds.
D) Background Writer; prevents Buffer Cache overflow.

### Question 11
What is a primary advantage of the Fractal Tree Index (or similar write-optimized B-tree variants) over a standard LSM-Tree?

A) Strictly O(1) point read performance without Bloom filters.
B) Better performance on range queries while maintaining high write throughput, as buffers are built into the internal nodes.
C) Zero write amplification.
D) Elimination of the need for a Write-Ahead Log (WAL).

## Section 4: Data Streaming & Delivery

### Question 12
Apache Kafka achieves extremely high throughput for consumers by utilizing "Zero-Copy" DMA (Direct Memory Access) transfers. Which underlying OS system call typically enables this by bypassing the application-level user space?

A) `sendfile()`
B) `epoll()`
C) `mmap()`
D) `fsync()`

### Question 13
Without Zero-Copy, delivering a file over a socket requires data to travel from the disk, to the OS page cache, to the application buffer (user space), to the socket buffer, and finally to the NIC buffer. How many context switches between user mode and kernel mode occur in this standard read/write path?

A) 1
B) 6
C) 2
D) 4

### Question 14
In Kafka, what guarantees that messages published to a specific partition will be consumed in the exact order they were sent by a single producer?

A) The producer attaches a monotonic timestamp to each message.
B) The consumer uses a priority queue to reorder messages upon receipt.
C) The producer connection maintains a strict sequence, and the partition log is an append-only structure that preserves this sequence.
D) The broker sorts messages before appending them to the log.

## Section 5: Time Series & Compression

### Question 15
The Gorilla paper from Facebook introduced a highly efficient compression scheme for time-series data. For the timestamp stream, what specific technique does Gorilla use?

A) Run-Length Encoding (RLE).
B) Huffman coding on absolute epoch timestamps.
C) Delta-of-Delta compression, encoding the difference between consecutive time deltas, which is often zero or very small for data collected at regular intervals.
D) Zstandard (Zstd) dictionary compression.

### Question 16
In Gorilla's floating-point value compression, if the XOR of the current value and the previous value is non-zero but the leading and trailing zero counts are the same as the previous XOR result, how is it encoded?

A) A control bit of `10`, followed immediately by the meaningful bits (reusing the previous leading/trailing zero counts).
B) A control bit of `1`, followed by the exact number of leading zeros, and then the meaningful bits.
C) A control bit of `11`, followed by the absolute float value.
D) A control bit of `0`, signifying no change.

### Question 17
Why is Delta-of-Delta compression less effective for event-driven time-series data (e.g., ad clicks) compared to infrastructural metrics (e.g., CPU usage)?

A) Event-driven data values change too rapidly.
B) Event-driven data occurs at irregular, unpredictable intervals, meaning the delta of deltas will rarely be zero and will require more bits to encode.
C) Event-driven data uses integers instead of floating-point numbers.
D) Event-driven systems do not use timestamps.

## Section 6: Advanced Storage Patterns

### Question 18
When implementing a distributed lock manager using a consensus protocol like Raft, a client acquires a lock and receives a lease. What mechanism prevents a delayed message from a "zombie" client (whose lease expired) from corrupting the protected resource?

A) The consensus leader blocks all writes until the zombie client recovers.
B) Fencing tokens: The lock manager issues a monotonically increasing token with the lock. The storage resource rejects any write request containing a token strictly less than the highest token it has seen.
C) The client utilizes a strictly synchronized atomic clock (TrueTime).
D) The lock manager sends a kill signal to the zombie client.

### Question 19
In Dynamo-style systems (like Cassandra), hinted handoff is used to improve write availability during temporary node failures. If Node A receives a write destined for Node B, but Node B is down, what does Node A do?

A) Rejects the write.
B) Changes the consistent hashing ring immediately to permanently exclude Node B.
C) Stores the write locally with a "hint" that it belongs to Node B, and forwards it to Node B when B recovers.
D) Broadcasts the write to all nodes in the cluster.

### Question 20
What is a major risk of relying on Hinted Handoff during a prolonged network partition or extended node outage?

A) The coordinating node (Node A) will run out of memory.
B) The hinted data becomes permanently immutable.
C) The consensus algorithm will trigger an infinite election loop.
D) The disk space on the coordinating node (Node A) can fill up with hints, leading to cascading failures, which is why hint storage is usually bounded or TTL-limited.
