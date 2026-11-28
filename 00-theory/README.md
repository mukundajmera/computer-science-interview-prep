# 📖 Theory & Fundamentals

This section covers the foundational concepts every software engineer should master before diving into design patterns and system design.

---

## 📚 Sections

| Section | Description | Difficulty |
|---------|-------------|------------|
| [OOP Principles](./oop-principles/) | SOLID, DRY, KISS, and core OOP concepts | ⭐ Beginner |
| [Distributed Systems](./distributed-systems/) | Distributed log storage, consensus | ⭐⭐⭐ Advanced |
| [System Design Fundamentals](./system-design-fundamentals/) | Basic building blocks of systems | ⭐⭐ Intermediate |
| [Database Concepts](./database-concepts/) | SQL, NoSQL, indexing, normalization | ⭐⭐ Intermediate |
| [Networking Basics](./networking-basics/) | HTTP, TCP/IP, REST, WebSockets | ⭐⭐ Intermediate |
| [Security & Auth](./security-and-auth/) | Practical cryptography, TLS 1.3, Auth | ⭐⭐ Intermediate |
| [Complexity Analysis](./complexity-analysis/) | Big O, time & space complexity | ⭐ Beginner |
| [Cheat Sheets](./cheat-sheets/) | Quick references & back-of-the-envelope numbers | ⭐ Beginner |
| [Data Structures](./data-structures/) | Spatial indexing, Quadtrees, Geohash, Hash Tables | ⭐⭐⭐ Advanced |
| [Big Data Structures](./big-data-structures/) | Bloom filters, HyperLogLog, LSM trees | ⭐⭐⭐ Advanced |
| [Distributed Systems](./distributed-systems/) | Write-Ahead Logs, LSM-trees | ⭐⭐⭐ Advanced |

---

## 🎯 Navigation Index

### [OOP Principles](./oop-principles/)
- [SOLID Principles](./oop-principles/solid-principles.md) - Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
- [Composition vs Inheritance](./oop-principles/composition-vs-inheritance.md) - When to use each
- [Encapsulation & Abstraction](./oop-principles/encapsulation-abstraction.md) - Data hiding and complexity hiding
- [DRY, KISS, YAGNI](./oop-principles/dry-kiss-yagni.md) - Essential design principles

### [System Design Fundamentals](./system-design-fundamentals/)
- [Deadlock Theory & Coffman Conditions](./concurrency/deadlock-theory-and-coffman-conditions.md) - Concurrency Safety
- [Client-Server Architecture](./system-design-fundamentals/client-server-architecture.md) - Foundation of distributed systems
- [Monolith vs Microservices](./system-design-fundamentals/monolith-vs-microservices.md) - Architecture patterns
- [Horizontal vs Vertical Scaling](./system-design-fundamentals/horizontal-vs-vertical-scaling.md) - Scaling strategies
- [Stateless vs Stateful](./system-design-fundamentals/stateless-vs-stateful.md) - State management
- [Synchronous vs Asynchronous](./system-design-fundamentals/sync-vs-async.md) - Communication patterns
- [CAP Theorem & Consistency Models](./system-design-fundamentals/cap-theorem.md) - Distributed consistency trade-offs
- [PACELC Theorem](./system-design-fundamentals/pacelc-theorem.md) - Latency vs Consistency trade-offs in normal operation
- [Back-of-Envelope Estimation](./system-design-fundamentals/back-of-envelope.md) - Interview capacity planning fundamentals
- [Concurrency in LLD](./system-design-fundamentals/concurrency-in-lld.md) - Correctness, coordination, and scarcity decisions
- [Memory Models & Cache Coherence](./system-design-fundamentals/memory-models-and-cache-coherence.md) - Hardware memory hierarchy, false sharing, and non-blocking mechanics
- [FLP Impossibility Result](./system-design-fundamentals/flp-impossibility.md) - Consensus limits in asynchronous systems with crash failures
- [Chandy-Lamport Distributed Snapshots](./system-design-fundamentals/distributed-snapshots-chandy-lamport.md) - Global state recording and consistent cuts without freezing
- [Byzantine Fault Tolerance](./system-design-fundamentals/byzantine-fault-tolerance.md) - BFT (PBFT, Tendermint) vs Crash Fault Tolerance (CFT)
- [Concurrency Paradigms](./system-design-fundamentals/concurrency-paradigms.md) - Shared Memory vs Actors vs CSP vs Reactive Streams
- [Lock-Free Data Structures & ABA](./concurrency/lock-free-data-structures-and-aba.md) - Herlihy hierarchy, Treiber Stack, Michael-Scott Queue, and ABA mitigation
- [Synchronization Primitives & Barriers](./concurrency/synchronization-primitives-and-barriers.md) - Mutexes, Semaphores, Memory Barriers, JMM vs Python GIL
- [Lock-Free Ring Buffers](./concurrency/ring-buffers.md) - SPSC/MPSC rings, power-of-two masking, cache-line padding, and acquire-release ordering
- [System Design Interview Delivery Framework](./system-design-fundamentals/system-design-interview-delivery-framework.md) - Structured 45-60 minute interview execution plan
- [Lambda vs. Kappa Architecture](./system-design-fundamentals/lambda-vs-kappa-architecture.md) - Batch + speed layers vs. single-log stream processing, reprocessing, and correctness drift

### [Distributed Systems](./distributed-systems/)
- [Paxos Consensus Variants](./distributed-systems/paxos-consensus-variants.md) - Paxos Consensus Protocols
- [2PC and 3PC](./distributed-systems/two-phase-and-three-phase-commit.md) - Two-Phase and Three-Phase Commit Protocols
- [CRDTs](./distributed-systems/crdt-conflict-free-replicated-data-types.md) - Conflict-Free Replicated Data Types
- [Quorum Consistency & Anti-Entropy](./distributed-systems/quorum-consistency-and-anti-entropy.md) - Hinted Handoff and Replication
- [Kafka Storage Internals](./distributed-systems/kafka-storage-internals.md) - Deep-dive into distributed log mechanics, zero-copy, and replication
- [Logical Time and Vector Clocks](./distributed-systems/logical-time-and-vector-clocks.md) - Time, Ordering, and Causality in Distributed Systems
- [Raft Consensus Protocol](./distributed-systems/raft-consensus-protocol.md) - Deep-dive into leader election, log replication, and Raft invariants
- [SWIM Gossip Protocol](./distributed-systems/swim-gossip-protocol.md) - Decentralized group membership, failure detection, and infection-style dissemination
- [WAL & LSM-Trees](./distributed-systems/wal-and-lsm-trees.md) - Storage engine internals, ARIES recovery, and the RUM conjecture

### [Database Concepts](./database-concepts/)
- [Database Normalization Theory](./database-concepts/database-normalization-theory.md) - Relational Normalization and Decomposition
- [B+ Tree Indexing & Latch Crabbing](./database-concepts/b-plus-tree-indexing-and-latch-crabbing.md) - Database internals for index concurrency
- [ARIES Recovery Algorithm](./database-concepts/aries-recovery-algorithm.md) - Transaction recovery
- [SQL vs NoSQL](./database-concepts/sql-vs-nosql.md) - Choosing the right database
- [ACID Properties](./database-concepts/acid-properties.md) - Transaction guarantees
- [Indexing](./database-concepts/indexing.md) - Query optimization
- [Data Modeling](./database-concepts/data-modeling.md) - Entities, relationships, schema evolution
- [Sharding](./database-concepts/sharding.md) - Horizontal database scaling
- [Replication](./database-concepts/replication.md) - High availability
- [The RUM Conjecture](./database-concepts/rum-conjecture.md) - Read, Update, Memory trade-off space for storage engines

### [Networking Basics](./networking-basics/)
- [HTTP/HTTPS](./networking-basics/http-https.md) - Web protocols
- [REST API Design](./networking-basics/rest-api-design.md) - API best practices
- [WebSockets](./networking-basics/websockets.md) - Real-time communication
- [gRPC](./networking-basics/grpc.md) - High-performance RPC
- [Networking Essentials](./networking-basics/networking-essentials.md) - Latency, throughput, routing, resiliency
- [TCP, UDP & Congestion Control](./networking-basics/tcp-udp-and-congestion-control.md) - Transport guarantees, handshake, reliability, congestion control

### [Security & Auth](./security-and-auth/)
- [Authentication & Sessions](./security-and-auth/authentication-sessions-and-jwts.md) - User Authentication, Session State, and Tokens
- [OAuth2 & OIDC](./security-and-auth/oauth2-and-oidc-protocols.md) - Delegated Authorization and Identity Protocols
- [Application Security](./security-and-auth/application-security-and-threat-modeling.md) - Threat Modeling & Defensive Engineering
- [Authorization (RBAC/ABAC/ReBAC)](./security-and-auth/authorization-rbac-abac-rebac.md) - Authorization Architectures like Google Zanzibar
- [Cryptography, TLS & Password Hashing](./security-and-auth/cryptography-tls-and-password-hashing.md) - Practical cryptography, TLS 1.3 protocol and modern credential storage

### [Complexity Analysis](./complexity-analysis/)
- [Big O Notation](./complexity-analysis/big-o-notation.md) - Time and space complexity
- [Common Algorithm Complexities](./complexity-analysis/common-complexities.md) - Sorting, searching, graphs

### [Cheat Sheets](./cheat-sheets/)
- [Complexity Reference](./cheat-sheets/complexity-reference.md) - Common data structure complexities
- [Design Tradeoffs](./cheat-sheets/design-tradeoffs.md) - Latency, availability, cost considerations
- [Interview Follow-ups](./cheat-sheets/interview-followups.md) - Probing questions by topic
- [LLD Patterns Guide](./cheat-sheets/lld-patterns-guide.md) - Quick lookup of pattern fit
- [Performance Numbers](./cheat-sheets/performance-numbers.md) - Latency/throughput back-of-the-envelope
### [Data Structures](./data-structures/)
- [Inverted Indexes & Roaring Bitmaps](./data-structures/inverted-indexes-and-roaring-bitmaps.md) - Search indexing and compressed bitsets
- [B-Trees and B+ Trees](./data-structures/b-trees-and-b-plus-trees.md) - Theoretical Foundation for Systems Design
- [Ring Buffers & Gorilla Compression](./data-structures/ring-buffers-and-gorilla-compression.md) - High-throughput queues and time-series compression
- [Spatial and Multidimensional Indexing](./data-structures/spatial-and-multidimensional-indexing.md) - Geohash, Quadtree, S2 Geometry, and R-Trees
- [Advanced Hash Tables](./data-structures/advanced-hash-tables.md) - Robin Hood, Hopscotch, Cuckoo, and Swiss Tables
- [Extended Big Data Structures Notes](./data-structures/big-data-structures.md) - Deeper notes including LSM trees, skip lists, and consistent hashing

### [Big Data Structures](./big-data-structures/)
- [Bloom Filter](./big-data-structures/README.md#1-bloom-filter) - Space-efficient membership testing with probabilistic false positives
- [HyperLogLog](./big-data-structures/README.md#2-hyperloglog) - Cardinality estimation for massive datasets
- [Count-Min Sketch](./big-data-structures/README.md#3-count-min-sketch) - Frequency estimation for streaming data
- [Approximate Quantiles](./big-data-structures/README.md#4-approximate-quantiles-t-digest--kll-style) - Percentile estimates for large streams
- [Reservoir Sampling](./big-data-structures/README.md#5-reservoir-sampling) - Fixed-memory sampling from unbounded streams
- [Merkle Tree](./big-data-structures/merkle-tree.md) - Efficient data verification and synchronization with hash-tree proofs
- [Trie](./big-data-structures/trie.md) - Prefix search, autocomplete, wildcard traversal, and radix-tree trade-offs


---

## 📋 Recommended Reading Order

For beginners, we recommend this sequence:

```
1. Complexity Analysis (understand how to analyze code)
   ↓
2. OOP Principles (foundation for all design)
   ↓
3. Networking Basics (how systems communicate)
   ↓
4. Database Concepts (how data is stored)
   ↓
5. System Design Fundamentals (putting it all together)
   ↓
6. Concurrency in LLD (before advanced project rounds)
```

---

## 🔗 Cross-References

| Theory Topic | Applied In |
|--------------|------------|
| SOLID Principles | All LLD Projects |
| Composition over Inheritance | Design Patterns (Decorator, Strategy) |
| Networking Essentials | HLD Concepts (Load Balancing, DNS, Service Discovery), Chat/Video systems |
| CAP Theorem & Consistency Models | [03-hld-concepts/cap-theorem/](../03-hld-concepts/cap-theorem/), multi-region write/read path design |
| Database Indexing | HLD Projects (Query optimization) |
| Sharding Fundamentals | [03-hld-concepts/database-sharding/](../03-hld-concepts/database-sharding/), Chat/Feed style scale-out systems |
| Performance Numbers | [resources/templates/practice-hld-core-concepts.md](../resources/templates/practice-hld-core-concepts.md), interview estimation drills |
| Data Modeling | HLD Projects (schema and partitioning decisions) |
| REST API Design | All HLD Projects |
| Complexity Analysis | Coding Problems, LLD optimization |
| Concurrency in LLD | [Movie Ticket Booking](../02-lld-projects/movie-ticket-booking/), [Rate Limiter](../02-lld-projects/rate-limiter/), [Job Scheduler](../02-lld-projects/job-scheduler/) |
| Lock-Free Data Structures & ABA | Concurrency, High-performance data structures |
| Synchronization Primitives & Barriers | Concurrency, Memory Models, Low-level synchronization |
| Trie | [Trie Coding Pack](../05-coding-problems/trie/README.md), autocomplete, command routing, prefix indexes |
| Merkle Tree | anti-entropy synchronization, audit logs, replicated storage consistency checks |
| Chandy-Lamport Snapshots | Distributed checkpointing, stream processing (Flink), deadlock detection |
| FLP Impossibility | Understanding consensus limitations in asynchronous networks |
| SWIM Gossip Protocol | Distributed consensus, Consul/Serf architecture, decentralized failure detection |

---

## ✅ Completion Checklist

- [ ] OOP Principles
  - [ ] Understand SOLID Principles
  - [ ] Understand Composition vs Inheritance
  - [ ] Understand Encapsulation & Abstraction
  - [ ] Understand DRY, KISS, YAGNI
- [ ] System Design Fundamentals
  - [ ] Understand Deadlock Theory & Coffman Conditions
  - [ ] Understand Client-Server Architecture
  - [ ] Understand Monolith vs Microservices
  - [ ] Understand Horizontal vs Vertical Scaling
  - [ ] Understand Stateless vs Stateful
  - [ ] Understand Synchronous vs Asynchronous
  - [ ] Understand CAP Theorem & Consistency Models
  - [ ] Understand PACELC Theorem
  - [ ] Understand Back-of-Envelope Estimation
  - [ ] Understand Concurrency in LLD
  - [ ] Understand Memory Models & Cache Coherence
  - [ ] Understand FLP Impossibility Result
  - [ ] Understand Chandy-Lamport Distributed Snapshots
  - [ ] Understand Byzantine Fault Tolerance
  - [ ] Understand Concurrency Paradigms
  - [ ] Understand Lock-Free Data Structures & ABA
  - [ ] Understand Synchronization Primitives & Barriers
  - [ ] Understand Lock-Free Ring Buffers
  - [ ] Understand System Design Interview Delivery Framework
- [ ] Distributed Systems
  - [ ] Understand Paxos Consensus Variants
  - [ ] Understand 2PC and 3PC
  - [ ] Understand CRDTs
  - [ ] Understand Quorum Consistency & Anti-Entropy
  - [ ] Understand Kafka Storage Internals
  - [ ] Understand Logical Time and Vector Clocks
  - [ ] Understand Raft Consensus Protocol
  - [ ] Understand SWIM Gossip Protocol
  - [ ] Understand WAL & LSM-Trees
- [ ] Database Concepts
  - [ ] Understand Database Normalization Theory
  - [ ] Understand B+ Tree Indexing & Latch Crabbing
  - [ ] Understand ARIES Recovery Algorithm
  - [ ] Understand SQL vs NoSQL
  - [ ] Understand ACID Properties
  - [ ] Understand Indexing
  - [ ] Understand Data Modeling
  - [ ] Understand Sharding
  - [ ] Understand Replication
  - [ ] Understand The RUM Conjecture
- [ ] Networking Basics
  - [ ] Understand HTTP/HTTPS
  - [ ] Understand REST API Design
  - [ ] Understand WebSockets
  - [ ] Understand gRPC
  - [ ] Understand Networking Essentials
  - [ ] Understand TCP, UDP & Congestion Control
- [ ] Security & Auth
  - [ ] Understand Authentication & Sessions
  - [ ] Understand OAuth2 & OIDC
  - [ ] Understand Application Security
  - [ ] Understand Authorization (RBAC/ABAC/ReBAC)
  - [ ] Understand Cryptography, TLS & Password Hashing
- [ ] Complexity Analysis
  - [ ] Understand Big O Notation
  - [ ] Understand Common Algorithm Complexities
- [ ] Cheat Sheets
  - [ ] Understand Complexity Reference
  - [ ] Understand Design Tradeoffs
  - [ ] Understand Interview Follow-ups
  - [ ] Understand LLD Patterns Guide
  - [ ] Understand Performance Numbers
- [ ] Data Structures
  - [ ] Understand Inverted Indexes & Roaring Bitmaps
  - [ ] Understand B-Trees and B+ Trees
  - [ ] Understand Ring Buffers & Gorilla Compression
  - [ ] Understand Spatial and Multidimensional Indexing
  - [ ] Understand Advanced Hash Tables
  - [ ] Understand Extended Big Data Structures Notes
- [ ] Big Data Structures
  - [ ] Understand Bloom Filter
  - [ ] Understand HyperLogLog
  - [ ] Understand Count-Min Sketch
  - [ ] Understand Approximate Quantiles
  - [ ] Understand Reservoir Sampling
  - [ ] Understand Merkle Tree
  - [ ] Understand Trie
---

## 🧭 Section Navigation

| | |
|---|---|
| **Prerequisites** | None — this is the starting point |
| **What's Next** | [Design Patterns →](../01-design-patterns/) — apply theory to proven solutions |
| **Related** | [CONCEPTS.md](../CONCEPTS.md) for a quick-reference cheatsheet<br>[LLD Interview Q&A](../02-lld-projects/INTERVIEW-QA.md) for LLD follow-ups<br>[LLD Interview Framework Quiz](../quizzes/lld-interview-framework-quiz.md) for delivery proficiency |

---

## 📌 Study Tips

1. **Don't skip theory** - It forms the foundation for everything else
2. **Take notes** - Write down key concepts in your own words
3. **Practice explaining** - Teach concepts to solidify understanding
4. **Apply immediately** - Use concepts in the next design pattern or project you study
