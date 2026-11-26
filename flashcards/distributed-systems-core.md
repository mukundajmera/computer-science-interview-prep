# Distributed Systems Core Flashcards

60 question-only flashcards for distributed systems interview execution.

---

## Consensus (Raft/Paxos) (12 Cards)

### Card 1
Front: How does Raft differ from Paxos in its approach to leader election?

### Card 2
Front: In Raft, what condition must a node satisfy to be elected leader during a term?

### Card 3
Front: What is the purpose of the 'term' number in Raft?

### Card 4
Front: How does Raft handle a network partition that splits the leader from the majority of the cluster?

### Card 5
Front: Describe the two phases of basic Paxos.

### Card 6
Front: How does Multi-Paxos optimize the basic Paxos protocol for continuous operation?

### Card 7
Front: What is a split vote in Raft and how is it resolved?

### Card 8
Front: In a Raft cluster of 5 nodes, how many nodes must be operational to maintain availability?

### Card 9
Front: Explain the concept of 'log matching property' in Raft.

### Card 10
Front: How does Raft handle log inconsistencies between a new leader and its followers?

### Card 11
Front: What happens in Paxos if multiple proposers try to propose values simultaneously?

### Card 12
Front: How do distributed systems typically use consensus algorithms in practice (e.g., Zookeeper, etcd)?

---

## Distributed Transactions (Saga/Outbox CDC) (12 Cards)

### Card 13
Front: What is the difference between a choreography-based and orchestration-based Saga?

### Card 14
Front: In a Saga pattern, what is a compensating transaction?

### Card 15
Front: Why is the Two-Phase Commit (2PC) protocol generally avoided in microservice architectures?

### Card 16
Front: What problem does the Transactional Outbox pattern solve?

### Card 17
Front: How does Change Data Capture (CDC) facilitate the Outbox pattern?

### Card 18
Front: In an orchestration-based Saga, how do you handle the failure of the orchestrator itself?

### Card 19
Front: What are the dual-write and read-your-own-writes problems in distributed systems?

### Card 20
Front: How can you achieve idempotency in distributed transaction compensation?

### Card 21
Front: Contrast the Saga pattern with the Try-Confirm/Cancel (TCC) pattern.

### Card 22
Front: What is a 'pivot transaction' in the context of a Saga?

### Card 23
Front: How do you handle a scenario where a compensating transaction repeatedly fails?

### Card 24
Front: What is 'semantic lock' in a Saga and why might it be necessary?

---

## Logical Clocks & Spanner TrueTime (12 Cards)

### Card 25
Front: What is the primary limitation of using physical clocks (wall-clock time) for ordering events in a distributed system?

### Card 26
Front: Define the 'happens-before' relationship in the context of logical clocks.

### Card 27
Front: How do Lamport Clocks work and what do they guarantee?

### Card 28
Front: What is the key advantage of Vector Clocks over Lamport Clocks?

### Card 29
Front: How do you detect a concurrent event using Vector Clocks?

### Card 30
Front: What is Google Spanner's TrueTime API?

### Card 31
Front: How does TrueTime represent a timestamp?

### Card 32
Front: How does Spanner use TrueTime to provide external consistency (linearizability)?

### Card 33
Front: What is 'commit wait' in Spanner and why is it necessary?

### Card 34
Front: How do Hybrid Logical Clocks (HLC) attempt to combine the benefits of physical and logical clocks?

### Card 35
Front: Why do Vector Clocks not scale well to systems with thousands of nodes?

### Card 36
Front: What happens in a system using Lamport Clocks if two concurrent events get the same timestamp?

---

## Live Database Sharding (12 Cards)

### Card 37
Front: What is the difference between range-based sharding and hash-based sharding?

### Card 38
Front: How does consistent hashing mitigate the impact of adding or removing a database node?

### Card 39
Front: What is a 'hot shard' and how can you resolve it?

### Card 40
Front: Describe the process of migrating data to a new shard without downtime (live sharding).

### Card 41
Front: In live sharding, what is the role of a 'routing tier' or proxy?

### Card 42
Front: How do you handle cross-shard transactions when migrating data during live sharding?

### Card 43
Front: What is 'directory-based sharding' and what are its trade-offs?

### Card 44
Front: How do you handle joins across tables that are sharded?

### Card 45
Front: Explain the double-write approach in a zero-downtime database migration.

### Card 46
Front: What is virtual node routing in consistent hashing?

### Card 47
Front: How do you ensure data consistency during the switch-over phase of a live shard migration?

### Card 48
Front: What is the impact of a poorly chosen shard key?

---

## Distributed Rate Limiting (12 Cards)

### Card 49
Front: Explain the Token Bucket rate limiting algorithm.

### Card 50
Front: How does the Leaky Bucket algorithm differ from Token Bucket?

### Card 51
Front: What is the Sliding Window Log rate limiting algorithm and what are its memory implications?

### Card 52
Front: How does the Sliding Window Counter algorithm balance accuracy and memory usage?

### Card 53
Front: Describe how to implement a distributed rate limiter using Redis.

### Card 54
Front: What is the 'thundering herd' problem in rate limiting and how do you mitigate it?

### Card 55
Front: How do you handle clock synchronization issues in distributed rate limiting?

### Card 56
Front: What are the trade-offs of using a local in-memory rate limiter versus a centralized Redis-based one?

### Card 57
Front: Explain how race conditions can occur in distributed rate limiting and how to prevent them.

### Card 58
Front: What is 'soft' vs 'hard' rate limiting?

### Card 59
Front: How would you implement IP-based rate limiting behind a CDN or Load Balancer?

### Card 60
Front: What metrics should you monitor for a distributed rate limiter?
