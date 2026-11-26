# Distributed Systems Core Quiz

40 multiple-choice questions focusing on edge cases, invariants, and trade-offs in distributed systems.

Time: 45 minutes
Difficulty: Hard

---

## Section 1: Consensus (Raft/Paxos) (8)

### Question 1
In a 5-node Raft cluster, network partition occurs, isolating the Leader (L) and one Follower (F1) from the other three nodes (F2, F3, F4). Which of the following is guaranteed to happen?

A) L continues to commit new entries.
B) F2, F3, and F4 will eventually elect a new leader.
C) The cluster becomes entirely unavailable for reads and writes.
D) F1 will become the new leader of the minority partition.

### Question 2
In Paxos, if a proposer receives promises from a majority of acceptors in Phase 1b, but none of the promises contain a previously accepted value, what should the proposer do in Phase 2a?

A) Propose its own value.
B) Abort the proposal and retry.
C) Propose a null value.
D) Wait for more promises.

### Question 3
What is the primary mechanism Raft uses to ensure the 'Leader Completeness' property (that a new leader has all committed entries from previous terms)?

A) A follower rejects a RequestVote RPC if its own log is more up-to-date than the candidate's.
B) The new leader forces followers to overwrite their uncommitted entries.
C) A background process continuously synchronizes logs between nodes.
D) The new leader contacts the old leader to fetch missing entries.

### Question 4
In Multi-Paxos, how is the overhead of Phase 1 (Prepare/Promise) minimized?

A) Phase 1 is skipped entirely.
B) A distinguished learner is used.
C) A stable leader runs Phase 1 once for all future instances.
D) Acceptors do not persist their state to disk.

### Question 5
In Raft, if a follower's log is inconsistent with the leader's log, how is consistency restored?

A) The follower deletes its entire log and copies the leader's log.
B) The leader sends empty AppendEntries to overwrite the follower's log.
C) The leader finds the latest point where the logs agree, deletes follower entries after that point, and sends its own entries.
D) The follower asks the leader for the specific missing entries.

### Question 6
Which scenario can cause a Raft cluster to fail to elect a leader indefinitely?

A) A network partition isolates one node.
B) Two nodes start an election at the exact same time with the exact same timeout.
C) A follower crashes and restarts.
D) The leader steps down gracefully.

### Question 7
In basic Paxos, what prevents an older proposal from overriding a newly decided value?

A) Acceptors promise not to accept proposals with lower proposal numbers.
B) Proposers cannot generate new proposal numbers once a value is decided.
C) The learner node rejects older proposals.
D) A centralized lock server coordinates proposals.

### Question 8
In Raft, when does a leader consider an entry 'committed'?

A) When it writes the entry to its own log.
B) When it sends the AppendEntries RPC to followers.
C) When it receives successful responses from a majority of nodes (including itself).
D) When all nodes have written the entry to their logs.

---

## Section 2: Distributed Transactions (Saga/Outbox CDC) (8)

### Question 9
In a microservices architecture using the Database-per-Service pattern, a business transaction spans Service A and Service B. Why is Two-Phase Commit (2PC) often a poor choice here?

A) It requires a distributed lock manager which is a single point of failure.
B) It blocks resources in multiple databases simultaneously, reducing throughput and availability during failures.
C) It cannot guarantee ACID properties.
D) Modern databases do not support XA transactions.

### Question 10
What is the primary function of the Transactional Outbox pattern?

A) To decouple inter-service communication using a message broker.
B) To ensure a database update and a message publish occur atomically.
C) To handle compensating transactions in a Saga.
D) To implement read-your-own-writes consistency.

### Question 11
In an orchestration-based Saga, Service A completes successfully, but Service B fails. Service A's compensating action is triggered but fails due to a temporary network issue. What is the most robust way to handle this?

A) Abort the Saga and manual intervention is required.
B) Retry the compensating action indefinitely with exponential backoff.
C) Rollback Service B's failure and try Service B again.
D) The orchestrator should ignore the failure and mark the Saga as complete.

### Question 12
When using Change Data Capture (CDC) to implement the Outbox pattern, what is a key advantage over polling the outbox table?

A) Lower latency in publishing messages.
B) Simpler implementation requiring fewer dependencies.
C) Eliminates the need for a separate message broker.
D) Guarantees exactly-once delivery.

### Question 13
In a choreography-based Saga, how do services know what to do?

A) They receive commands from a central orchestrator.
B) They listen to domain events published by other services.
C) They periodically poll each other's databases.
D) They use distributed tracing to follow the transaction flow.

### Question 14
What is the 'dual-write' problem that the Outbox pattern solves?

A) Writing to a master and a replica database simultaneously.
B) Updating a database and publishing to a message broker, where one might succeed and the other fail.
C) Writing to two different tables within the same database transaction.
D) Two concurrent requests attempting to update the same row.

### Question 15
Which of the following is a critical requirement for compensating transactions in a Saga?

A) They must execute instantaneously.
B) They must be idempotent.
C) They must not access the database.
D) They must use a different protocol than the original transaction.

### Question 16
What happens if the Saga Orchestrator crashes midway through executing a Saga?

A) All active Sagas are permanently stuck.
B) The orchestrator state must be recovered from a persistent store upon restart to resume execution.
C) The participating services will automatically roll back their local transactions.
D) A backup orchestrator immediately takes over via active-active replication.

---

## Section 3: Logical Clocks & Spanner TrueTime (8)

### Question 17
In a distributed system, event A happens on node 1 and event B happens on node 2. Both nodes use wall-clock time (NTP). Node 1 records t(A) = 10:00:00 and Node 2 records t(B) = 10:00:01. Can you conclude that A caused B?

A) Yes, because t(A) < t(B).
B) No, because wall-clocks can suffer from clock skew.
C) Yes, if NTP is configured to sync every second.
D) No, because causality cannot be inferred from timestamps.

### Question 18
Given a Lamport Clock system, if event A happens before event B (A -> B), which of the following is ALWAYS true?

A) L(A) < L(B)
B) L(A) > L(B)
C) A and B occurred on the same node.
D) B was caused by A.

### Question 19
Given Lamport Clocks L(A) = 3 and L(B) = 5, what can you definitively say about the relationship between A and B?

A) A happened before B.
B) B happened before A.
C) They are concurrent.
D) Nothing; L(A) < L(B) does not imply A -> B.

### Question 20
In Vector Clocks, node 1 has vector [2, 0, 0] and node 2 has vector [1, 2, 0]. What is the relationship between their current states?

A) Node 1 happened before Node 2.
B) Node 2 happened before Node 1.
C) They are concurrent (neither happened before the other).
D) They are identical.

### Question 21
What does the TrueTime API (TT.now()) in Google Spanner return?

A) A single highly accurate integer timestamp.
B) An interval [earliest, latest] representing the uncertainty window.
C) A vector clock array.
D) A Lamport timestamp combined with a node ID.

### Question 22
How does Spanner use TrueTime to guarantee external consistency (linearizability) for read-write transactions?

A) The transaction coordinator waits until TT.now().earliest > commit_timestamp before replying to the client.
B) It uses a distributed lock manager across all datacenters.
C) It forces all clocks to synchronize to the exact microsecond before committing.
D) It uses Paxos to agree on the exact time of the commit.

### Question 23
What is the primary drawback of Vector Clocks in systems with a high churn of nodes (nodes frequently joining and leaving)?

A) They cannot detect causality.
B) The vector size grows unbounded, leading to high storage and network overhead.
C) They require perfectly synchronized physical clocks.
D) They are only suitable for synchronous networks.

### Question 24
What do Hybrid Logical Clocks (HLC) attempt to solve?

A) They eliminate the need for vector clocks entirely.
B) They provide a Lamport-like clock that stays close to the physical time, allowing for both causality tracking and meaningful time queries.
C) They guarantee perfectly synchronized physical clocks across all nodes.
D) They replace Spanner's TrueTime API for open-source databases.

---

## Section 4: Live Database Sharding (8)

### Question 25
When migrating data to a new sharded database with zero downtime, what is typically the first step in the migration process?

A) Change the application to read from the new database.
B) Implement dual-writes to both the old and new databases.
C) Run a bulk copy of the existing data from the old to the new database.
D) Delete the old database.

### Question 26
During a live migration using dual-writes, how do you handle data that was modified in the old database *before* the bulk copy finished, but *after* the bulk copy started?

A) Ignore it; eventual consistency will resolve it.
B) Re-run the entire bulk copy.
C) Ensure the bulk copy process captures or replays ongoing changes (CDC/binlog), or use a rolling window approach.
D) Stop all writes during the bulk copy.

### Question 27
What is a major advantage of Consistent Hashing over simple Modulo hashing (key % N) for sharding?

A) It provides perfectly uniform data distribution.
B) It eliminates the need for a routing tier.
C) When adding or removing a node, only a small fraction of keys (roughly 1/N) need to be remapped.
D) It allows for cross-shard transactions without 2PC.

### Question 28
In a sharded architecture, what is a 'scatter-gather' query?

A) A query that updates the routing table.
B) A query that requires routing to multiple shards and aggregating the results in the application or proxy tier.
C) A query that only targets a specific hot shard.
D) A background process that rebalances data.

### Question 29
Why are 'virtual nodes' (vnodes) used in Consistent Hashing?

A) To improve security by masking physical node IPs.
B) To reduce the number of physical servers needed.
C) To improve the uniformity of data distribution across heterogeneous servers.
D) To handle transactions across different databases.

### Question 30
During a live sharding migration, if the application is reading from the new database but encounters a missing record, what is a common fallback strategy?

A) Return an error to the user.
B) Wait and retry the read.
C) Read from the old database and asynchronously copy it to the new database (read-repair).
D) Assume the record was deleted.

### Question 31
What is a significant drawback of Directory-Based Sharding (using a lookup table to map keys to shards)?

A) The directory becomes a single point of failure and a potential bottleneck.
B) It cannot handle non-integer shard keys.
C) It requires all data to be stored on a single node.
D) It forces the use of Consistent Hashing.

### Question 32
How do you resolve a 'hot shard' problem where one tenant generates 80% of the traffic?

A) Increase the number of virtual nodes.
B) Use a different hashing algorithm.
C) Isolate the heavy tenant to its own dedicated shard(s) or use a composite shard key (e.g., tenant_id + entity_id).
D) Add more nodes and perform modulo hashing.

---

## Section 5: Distributed Rate Limiting (8)

### Question 33
In the Token Bucket algorithm, what happens if a request arrives and the bucket is empty?

A) The request is buffered indefinitely.
B) The request is dropped or rejected (rate limited).
C) The bucket size is temporarily increased.
D) The token refill rate is increased.

### Question 34
Why might a centralized rate limiter using Redis (e.g., using INCR and EXPIRE) suffer under extremely high concurrent load?

A) Redis cannot handle integer increments.
B) It introduces network latency and Redis can become a bottleneck (hot key problem).
C) Redis does not support atomic operations.
D) Expire times in Redis are inaccurate.

### Question 35
How does the Sliding Window Log algorithm handle bursts of traffic compared to the Fixed Window Counter algorithm?

A) It is less accurate and allows more bursts.
B) It drops all burst traffic.
C) It provides a more accurate rate limit by tracking the exact timestamp of every request, preventing bursts at the edges of fixed windows.
D) It uses less memory than the Fixed Window Counter.

### Question 36
What is the main disadvantage of the Sliding Window Log algorithm?

A) It is inaccurate for low-volume traffic.
B) It consumes significant memory to store the timestamp of every request.
C) It cannot be implemented in Redis.
D) It requires complex mathematical calculations.

### Question 37
To solve the memory issue of Sliding Window Log and the inaccuracy of Fixed Window Counter, what does the Sliding Window Counter algorithm do?

A) It uses a single token bucket.
B) It uses leaky buckets arranged in a ring buffer.
C) It uses a weighted average of the previous window's count and the current window's count based on the overlap percentage.
D) It randomly drops requests during high load.

### Question 38
In a distributed environment, implementing rate limiting in a centralized Redis store can lead to race conditions (e.g., read-modify-write). How can this be reliably prevented?

A) By using client-side locks.
B) By evaluating the rate limiting logic within a Redis Lua script to ensure atomicity.
C) By relying on NTP for clock synchronization.
D) By using a local in-memory cache instead.

### Question 39
What is a common strategy to mitigate the performance impact of a centralized Redis rate limiter?

A) Switch to a relational database.
B) Use local in-memory rate limiters on each application node, accepting less strict global accuracy for better performance.
C) Increase the size of the token bucket.
D) Use a single-threaded application server.

### Question 40
When rate limiting based on IP address behind a Load Balancer or CDN, which HTTP header is commonly used to identify the true client IP?

A) User-Agent
B) Host
C) X-Forwarded-For
D) Authorization
