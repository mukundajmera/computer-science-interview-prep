# Distributed Storage & Consensus Quiz - Answer Key

## Answers

1. D
2. B
3. C
4. A
5. B
6. A
7. D
8. C
9. D
10. A
11. B
12. A
13. D
14. C
15. C
16. A
17. B
18. B
19. C
20. D

---

## Detailed Explanations

### Section 1: Consensus & Snapshots

1. **D**: In Raft, a leader only commits an entry once it is replicated to a majority of nodes (A, B, C in this case). Even though A crashed, Node B and Node C both have the entry. Node B's log is as up-to-date as a majority of the cluster. The RequestVote RPC requires voters to check log recency. Because B's log is up-to-date, it can secure votes from C and possibly D or E (if they participate), preserving the committed entry X.
2. **B**: Raft's election restriction states that a voter denies a vote if its own log is more up-to-date than the candidate's. Up-to-date is defined primarily by the term of the last entry. Since F's last entry term (4) is greater than G's (3), F's log is more up-to-date, regardless of the index length. Node F must deny the vote.
3. **C**: The Chandy-Lamport snapshot algorithm specifies that upon receiving a marker on a channel for the *first time*, a process must record its own local state and immediately begin recording all incoming messages on all *other* incoming channels until a marker is received on those respective channels.
4. **A**: Messages that are "in transit" are precisely what the algorithm captures by recording incoming messages on a channel between the time the local state is recorded and the time the marker arrives on that specific channel. The algorithm assumes FIFO channels to ensure the marker arrives exactly after the messages sent before it.

### Section 2: Distributed Transactions

5. **B**: This is the classic "Blocking Coordinator Failure" of Two-Phase Commit. Participant P1 is in the `PREPARED` state, meaning it has acquired locks and promised to be able to commit or abort. Without the coordinator's final decision, P1 cannot safely guess the outcome and must block indefinitely, holding resources until recovery.
6. **A**: In a Saga, because Service A and Service B have already committed their local transactions to their databases, a standard rollback cannot undo them. The Orchestrator must issue explicit application-level compensating commands (e.g., if A was "Debit $100", the compensation is "Credit $100") to logically reverse the actions of B and then A.
7. **D**: Compensating transactions must be idempotent. If a network failure occurs during compensation, the orchestrator's only recourse is to retry the command. If the compensation is not idempotent, retries could lead to duplicate reversals (e.g., crediting $100 multiple times).

### Section 3: Storage Engine Trade-offs

8. **C**: In an LSM-Tree (like RocksDB), Level 0 (L0) files are created by flushing MemTables directly to disk. Because they represent sequential time windows of writes, their key ranges can and do overlap. When L0 is compacted into Level 1 (L1), the data is merge-sorted, ensuring that all SSTables within L1 (and L2, L3, etc.) have disjoint, non-overlapping key ranges.
9. **D**: Leveled compaction heavily favors read performance and space efficiency at the cost of high Write Amplification. As data is continually read, merged, and rewritten from one level to the next (e.g., L1 to L2, L2 to L3), a single application byte may be rewritten to disk 10-30 times.
10. **A**: PostgreSQL's Autovacuum is essential for managing MVCC. Every row version is tagged with a transaction ID (XID). Because XIDs are 32-bit integers, they eventually wrap around. Autovacuum reclaims space from dead tuples (preventing bloat) and "freezes" old tuples, marking them as permanently visible to prevent XID wraparound, which would otherwise hide historical data.
11. **B**: Fractal Trees (or Be-Trees) integrate message buffers into their internal tree nodes. This allows them to ingest writes quickly (like an LSM-Tree) by buffering them, but they maintain a tree structure that supports efficient O(log N) range queries without the need to read across multiple distinct files or levels.

### Section 4: Data Streaming & Delivery

12. **A**: The `sendfile()` system call allows data to be transferred directly from the OS page cache to the network socket buffer, entirely bypassing the application (user space) buffer. This is known as "Zero-Copy" and drastically reduces CPU overhead and context switching.
13. **D**: A standard non-zero-copy transfer requires four context switches: (1) user to kernel mode for `read()`, (2) kernel to user mode returning the data, (3) user to kernel mode for `write()`, and (4) kernel to user mode returning from the socket write.
14. **C**: Kafka maintains strict ordering per partition for a single producer because the producer client sequences the messages, and the broker appends them to a strictly append-only log file. As long as the producer does not have concurrent unacknowledged in-flight requests (or handles them correctly with idempotency/sequence IDs), the log order reflects the send order.

### Section 5: Time Series & Compression

15. **C**: Gorilla utilizes Delta-of-Delta compression for timestamps. Since time-series metrics are often scraped at regular intervals (e.g., every 60 seconds), the delta between timestamps is mostly constant (60). The delta *of those deltas* is therefore exactly zero, which can be encoded in a single bit.
16. **A**: When compressing floating-point values via XOR, if the current XOR value shares the same leading and trailing zero counts as the previous XOR value, Gorilla optimizes this by using a `10` control sequence, avoiding the need to explicitly encode the leading zero count, and immediately outputting the meaningful bits.
17. **B**: Delta-of-Delta relies on constant intervals to produce zeros. Event-driven data occurs sporadically. The time delta between event 1 and 2 might be 5 seconds, and between 2 and 3 might be 300 seconds. The delta-of-deltas is non-zero, requiring significantly more bits to encode the unpredictable variances.

### Section 6: Advanced Storage Patterns

18. **B**: Fencing tokens solve the zombie client problem. The lock manager issues a monotonic token (e.g., 5). The storage service tracks the highest token seen. If a delayed write from a client holding token 3 arrives after the lock was reassigned (token 5), the storage service rejects it because 3 < 5.
19. **C**: Hinted handoff allows the system to remain highly available for writes. The coordinating node accepts the write, stores it locally with a "hint" indicating its true destination, and takes responsibility for delivering the write to Node B once B's availability is restored.
20. **D**: If Node B is down for days, Node A will accumulate massive amounts of hints. This can exhaust Node A's disk space or severely degrade its performance, causing cascading failures across the cluster. Modern systems impose strict size or time limits (TTLs) on hinted handoff buffers.
