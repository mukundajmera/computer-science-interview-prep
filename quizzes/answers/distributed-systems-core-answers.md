# Distributed Systems Core Quiz - Answer Key

## Answers

1. B
2. A
3. A
4. C
5. C
6. B
7. A
8. C
9. B
10. B
11. B
12. A
13. B
14. B
15. B
16. B
17. B
18. A
19. D
20. C
21. B
22. A
23. B
24. B
25. C
26. C
27. C
28. B
29. C
30. C
31. A
32. C
33. B
34. B
35. C
36. B
37. C
38. B
39. B
40. C

---

## Detailed Explanations

### Section 1: Consensus (Raft/Paxos)
1. **B**: The isolated nodes (F2, F3, F4) form a majority (3 out of 5) and will time out and elect a new leader. The old leader (L) and F1 cannot commit anything because they cannot reach a majority.
2. **A**: If no previous value has been accepted (all promises return null values), the proposer is free to propose its own value in Phase 2a.
3. **A**: Raft ensures the Leader Completeness property by making followers reject RequestVote RPCs if the candidate's log is less up-to-date than the follower's. This guarantees the elected leader has all committed entries.
4. **C**: Multi-Paxos optimizes by electing a stable leader. This leader performs Phase 1 only once. For all subsequent proposals, it can jump straight to Phase 2, reducing latency.
5. **C**: The Raft leader finds the latest entry where the logs agree, sends an AppendEntries RPC that overwrites any conflicting entries on the follower after that point, and appends the leader's entries.
6. **B**: If multiple nodes start an election simultaneously and have the same timeout, they might repeatedly split the vote, preventing a majority from forming. Raft mitigates this with randomized timeouts.
7. **A**: In Phase 1b, acceptors promise to reject any future proposals with a lower proposal number. This prevents older proposals from overwriting a decided value.
8. **C**: A leader considers an entry committed once it has safely replicated the entry to a majority of the servers in the cluster.

### Section 2: Distributed Transactions (Saga/Outbox CDC)
9. **B**: 2PC is synchronous and blocks resources (locks) across multiple databases until the transaction completes or fails. This significantly degrades throughput and availability, especially when network partitions occur.
10. **B**: The Outbox pattern ensures that updating local database state and publishing an event/message about that update occur atomically, avoiding the dual-write problem.
11. **B**: Compensating actions in a Saga must eventually succeed. If they fail due to transient errors, the system must retry them. This requires the compensating actions to be idempotent.
12. **A**: CDC (reading from the transaction log) is typically faster (lower latency) and less resource-intensive than continuously polling an outbox table via SQL queries.
13. **B**: In a choreography Saga, there is no central controller. Services subscribe to domain events published by other services and react accordingly to progress the transaction.
14. **B**: The dual-write problem is the challenge of atomically updating a local database and publishing a message to a message broker. Without 2PC or Outbox, one operation can succeed while the other fails.
15. **B**: Compensating transactions must be idempotent because they might need to be retried multiple times in the event of transient failures during the compensation phase.
16. **B**: The orchestrator must be durable. Its state (which steps have completed) must be persisted so that if it crashes, it can recover and resume the Saga from where it left off.

### Section 3: Logical Clocks & Spanner TrueTime
17. **B**: Wall-clock time across different nodes cannot reliably establish causality due to clock skew and drift. NTP cannot guarantee perfectly synchronized clocks.
18. **A**: If A happens before B (A -> B), Lamport Clocks guarantee that L(A) < L(B). The converse is not true; L(A) < L(B) does not necessarily mean A -> B (they could be concurrent).
19. **D**: A Lamport clock value being smaller (L(A) < L(B)) does not imply A happened before B. They could be concurrent events where A happened to get a smaller timestamp.
20. **C**: Because node 1's vector is greater in the first index (2 > 1) but node 2's vector is greater in the second index (2 > 0), the vectors are not strictly greater than or less than each other. This indicates concurrent events.
21. **B**: TrueTime returns an interval `[earliest, latest]` that bounds the uncertainty of the local clock. The actual time is guaranteed to be within this interval.
22. **A**: To guarantee external consistency, Spanner's commit wait ensures that the transaction coordinator does not respond to the client until the TrueTime interval has passed the transaction's commit timestamp (i.e., `TT.now().earliest > commit_timestamp`).
23. **B**: In Vector Clocks, each node ID requires an entry in the vector. With many ephemeral nodes, the vector grows indefinitely, adding significant overhead to every message and storage.
24. **B**: HLCs provide logical timestamps (for causality) but keep them close to the physical time (for meaningful time-based queries), bridging the gap between Lamport Clocks and wall clocks.

### Section 4: Live Database Sharding
25. **C**: The first step is typically to bulk copy (bootstrap) the existing data from the source to the new sharded destination.
26. **C**: The migration process must capture changes (e.g., using CDC or binlogs) that occur during the bulk copy and replay them on the new database to achieve eventual consistency before the final cutover.
27. **C**: Consistent hashing minimizes data movement. When a node is added or removed, only the keys belonging to that node's segment of the hash ring are remapped, rather than remapping nearly all keys as in modulo hashing.
28. **B**: A scatter-gather query is one that cannot be satisfied by a single shard (e.g., a query not filtering on the shard key). It must be sent to multiple (or all) shards and the results combined.
29. **C**: Virtual nodes (vnodes) map multiple points on the hash ring to a single physical server. This helps distribute data more uniformly and allows weighting servers based on their capacity.
30. **C**: The read-repair (or lazy migration) strategy involves attempting to read from the new DB; if not found, read from the old DB, write it to the new DB, and return the result to the client.
31. **A**: Directory-based sharding requires a lookup service. This service must be highly available and performant, as every query must query the directory first.
32. **C**: A hot shard cannot be resolved by simply changing the hashing algorithm if a single key (e.g., one huge tenant) generates the load. You must isolate that tenant or use a composite key to further shard their data.

### Section 5: Distributed Rate Limiting
33. **B**: In the Token Bucket algorithm, if a request arrives and no tokens are available, the request is rejected or dropped.
34. **B**: A centralized Redis rate limiter can become a bottleneck because every request from every server must make a network call to Redis, potentially causing high latency and creating a 'hot key' if a single IP or user is heavily limited.
35. **C**: Fixed window allows 2x the limit if bursts occur at the end of one window and the beginning of the next. Sliding Window Log precisely tracks request timestamps, preventing these edge-case bursts.
36. **B**: The Sliding Window Log must store the timestamp of *every* request in the current window. For high-volume APIs, this consumes a massive amount of memory.
37. **C**: The Sliding Window Counter approximates the sliding window by taking a weighted sum of the previous window's count and the current window's count, requiring very little memory while smoothing out bursts.
38. **B**: To perform read-modify-write operations atomically in Redis (like checking a count and then incrementing it), you must use a Lua script. Redis executes Lua scripts atomically.
39. **B**: To improve performance, systems often use local in-memory rate limiters (e.g., Guava RateLimiter) on the application servers. They might sync counts periodically with a central store, trading strict accuracy for lower latency.
40. **C**: The `X-Forwarded-For` HTTP header is the standard way to identify the originating IP address of a client connecting through an HTTP proxy or load balancer.
