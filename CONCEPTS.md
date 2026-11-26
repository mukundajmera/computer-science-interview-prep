# 📖 Concepts Quick Reference

A comprehensive quick reference cheatsheet for all major concepts covered in this repository.

---

## 📑 Table of Contents

- [🎨 Design Patterns Summary](#-design-patterns-summary)
- [🔧 LLD vs HLD](#-lld-vs-hld)
- [🧵 Concurrency in LLD](#-concurrency-in-lld)
- [📋 LLD Projects Index](#-lld-projects-index)
- [📊 Common Complexity Classes](#-common-complexity-classes)
- [🗺️ System Design Components Map](#️-system-design-components-map)
- [🌳 Decision Trees](#-decision-trees)
- [🔑 Key Theorems & Concepts](#-key-theorems--concepts)
- [📐 Back-of-Envelope Numbers](#-back-of-envelope-numbers)
- [🔗 Cross-Reference Guide](#-cross-reference-guide)
- [🤖 Generative AI System Design](#-generative-ai-system-design)

---

## 🎨 Design Patterns Summary

<a id="creational-patterns"></a>

### Creational Patterns (5)
*Deal with object creation mechanisms*

| Pattern | One-Liner | Use When | Link |
|---------|-----------|----------|------|
| **Singleton** | Ensures only one instance exists | Database connections, Config managers, Logging | [→](./01-design-patterns/creational/) |
| **Factory Method** | Creates objects without specifying class | Multiple product types, Plugin systems | [→](./01-design-patterns/creational/) |
| **Abstract Factory** | Creates families of related objects | Cross-platform UI, Theme systems | [→](./01-design-patterns/creational/) |
| **Builder** | Constructs complex objects step-by-step | Objects with many optional parameters (4+) | [→](./01-design-patterns/creational/) |
| **Prototype** | Clones existing objects | Expensive object creation, Caching templates | [→](./01-design-patterns/creational/) |

### Structural Patterns (7)
*Deal with object composition*

| Pattern | One-Liner | Use When | Link |
|---------|-----------|----------|------|
| **Adapter** | Makes incompatible interfaces work together | Legacy system integration, Third-party APIs | [→](./01-design-patterns/structural/adapter/) |
| **Bridge** | Separates abstraction from implementation | Multi-platform support, Vary independently | [→](./01-design-patterns/structural/bridge/) |
| **Composite** | Treats objects and compositions uniformly | Tree structures, UI components, File systems | [→](./01-design-patterns/structural/composite/) |
| **Decorator** | Adds behavior dynamically | Feature toggles, Middleware, Wrappers | [→](./01-design-patterns/structural/decorator/) |
| **Facade** | Provides simplified interface | Complex subsystem access, Library wrappers | [→](./01-design-patterns/structural/facade/) |
| **Flyweight** | Shares common state between objects | Large number of similar objects, Memory optimization | [→](./01-design-patterns/structural/flyweight/) |
| **Proxy** | Controls access to another object | Lazy loading, Access control, Caching | [→](./01-design-patterns/structural/proxy/) |

### Behavioral Patterns (11)
*Deal with object communication*

| Pattern | One-Liner | Use When | Link |
|---------|-----------|----------|------|
| **Chain of Responsibility** | Passes request along handler chain | Request pipelines, Middleware, Approval workflows | [→](./01-design-patterns/behavioral/chain-of-responsibility/) |
| **Command** | Encapsulates request as object | Undo/redo, Task queuing, Macro recording | [→](./01-design-patterns/behavioral/command/) |
| **Interpreter** | Defines grammar representation | DSLs, Simple parsers | [→](./01-design-patterns/behavioral/interpreter/) |
| **Iterator** | Traverses collection without exposing internals | Custom collections, Tree traversal | [→](./01-design-patterns/behavioral/iterator/) |
| **Mediator** | Centralizes complex communication | Chat rooms, Air traffic control, Dialog boxes | [→](./01-design-patterns/behavioral/mediator/) |
| **Memento** | Captures and restores object state | Undo functionality, Checkpoints, Save game | [→](./01-design-patterns/behavioral/memento/) |
| **Observer** | Notifies dependents of state changes | Event systems, Pub/sub, UI updates | [→](./01-design-patterns/behavioral/observer/) |
| **State** | Alters behavior when state changes | Workflow engines, Game states, Vending machines | [→](./01-design-patterns/behavioral/state/) |
| **Strategy** | Defines interchangeable algorithms | Payment methods, Sorting options, Pricing | [→](./01-design-patterns/behavioral/strategy/) |
| **Template Method** | Defines algorithm skeleton | Framework hooks, Fixed process with variations | [→](./01-design-patterns/behavioral/template-method/) |
| **Visitor** | Separates algorithm from object structure | Report generation, Serialization, Operations on trees | [→](./01-design-patterns/behavioral/visitor/) |

### 🎯 Pattern Quick Decision

```
Need to create objects?
├── Exactly one instance? → Singleton
├── Without specifying class? → Factory Method
├── Families of related objects? → Abstract Factory
├── Complex with many params? → Builder
└── Clone existing? → Prototype

Need to compose/structure objects?
├── Make incompatible work? → Adapter
├── Separate abstraction? → Bridge
├── Tree structure uniformly? → Composite
├── Add behavior dynamically? → Decorator
├── Simplify complex subsystem? → Facade
├── Share state for memory? → Flyweight
└── Control access? → Proxy

Need objects to communicate?
├── Notify many of changes? → Observer
├── Swap algorithms at runtime? → Strategy
├── Behavior changes with state? → State
├── Encapsulate as object? → Command
├── Pass along handlers? → Chain of Responsibility
├── Algorithm skeleton? → Template Method
└── Capture/restore state? → Memento
```

---

## 🔧 LLD vs HLD

| Aspect | Low-Level Design (LLD) | High-Level Design (HLD) |
|--------|------------------------|------------------------|
| **Focus** | Classes, methods, relationships | Components, services, data flow |
| **Scale** | Single application | Distributed systems |
| **Output** | Class diagrams, code | Architecture diagrams |
| **Concerns** | OOP, patterns, clean code | Scalability, availability, consistency |
| **Interview Time** | 45-60 minutes | 45-60 minutes |
| **Examples** | Parking Lot, Chess Game, Elevator | Twitter, URL Shortener, Uber |
| **Key Skills** | SOLID principles, Design patterns | CAP theorem, Trade-offs |

### When to Use Which Approach

```
LLD Questions typically include:
├── "Design a [specific application]"
├── Class-level design focus
├── OOP principles matter
├── Implementation details important
└── Usually simpler scale

HLD Questions typically include:
├── "Design a system like [company/product]"
├── "Millions of users" mentioned
├── Scale and distribution focus
├── Trade-offs discussion expected
└── Architecture diagram required
```

---

## 🧵 Concurrency in LLD

| Lens | Core Question | Typical Primitive | Project Anchor |
|------|---------------|-------------------|----------------|
| Correctness | Can concurrent updates break an invariant? | Atomic critical section, CAS/version check | [Movie Ticket Booking](./02-lld-projects/movie-ticket-booking/) |
| Coordination | How do producers/consumers hand off work safely? | Bounded queue, worker-pool admission policy | [Job Scheduler](./02-lld-projects/job-scheduler/) |
| Scarcity | How do we govern finite permits/capacity? | Semaphore/permit gate, token budget | [Rate Limiter](./02-lld-projects/rate-limiter/) |

Reference: [Concurrency in LLD](./00-theory/system-design-fundamentals/concurrency-in-lld.md)

---

## 📋 LLD Projects Index

| Project | Complexity | Key Patterns | Key Concepts | Est. Time | Link |
|---------|------------|--------------|--------------|-----------|------|
| **Parking Lot** | ⭐⭐ | [Factory](./01-design-patterns/creational/factory-method/), [Strategy](./01-design-patterns/behavioral/strategy/), [Singleton](./01-design-patterns/creational/singleton/) | Multi-level, Pricing, Concurrency | 60 min | [→](./02-lld-projects/parking-lot/) |
| **Amazon Locker** | ⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [State](./01-design-patterns/behavioral/state/) | Compartment allocation, token lifecycle, reservation workflow | 60 min | [→](./02-lld-projects/amazon-locker/) |
| **LRU Cache** | ⭐⭐ | - | HashMap + LinkedList, O(1) ops | 45 min | [→](./02-lld-projects/lru-cache/) |
| **Elevator System** | ⭐⭐⭐ | [State](./01-design-patterns/behavioral/state/), [Strategy](./01-design-patterns/behavioral/strategy/), [Observer](./01-design-patterns/behavioral/observer/) | Scheduling, State machines | 90 min | [→](./02-lld-projects/elevator-system/) |
| **Library Management** | ⭐⭐ | [Factory](./01-design-patterns/creational/factory-method/), [Observer](./01-design-patterns/behavioral/observer/) | Borrowing, Reservations | 60 min | [→](./02-lld-projects/library-management/) |
| **Vending Machine** | ⭐⭐ | [State](./01-design-patterns/behavioral/state/), [Strategy](./01-design-patterns/behavioral/strategy/) | State transitions, Payment | 45 min | [→](./02-lld-projects/vending-machine/) |
| **ATM System** | ⭐⭐⭐ | [State](./01-design-patterns/behavioral/state/), [Chain of Responsibility](./01-design-patterns/behavioral/chain-of-responsibility/) | Transactions, State machines | 75 min | [→](./02-lld-projects/atm-system/) |
| **Chess Game** | ⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [Command](./01-design-patterns/behavioral/command/) | Move validation, Game logic | 90 min | [→](./02-lld-projects/chess-game/) |
| **Hotel Reservation** | ⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [Observer](./01-design-patterns/behavioral/observer/) | Booking, Pricing, Concurrency | 75 min | [→](./02-lld-projects/hotel-reservation/) |
| **Movie Ticket Booking** | ⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [Observer](./01-design-patterns/behavioral/observer/) | Seat selection, payment, lock ownership boundaries | 75 min | [→](./02-lld-projects/movie-ticket-booking/) |
| **Snake & Ladder** | ⭐⭐ | [State](./01-design-patterns/behavioral/state/), [Strategy](./01-design-patterns/behavioral/strategy/) | Game rules, Turn management | 60 min | [→](./02-lld-projects/snake-and-ladder/) |
| **Tic-Tac-Toe** | ⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/) | Win detection, Turn management | 45 min | [→](./02-lld-projects/tic-tac-toe/) |
| **Connect Four** | ⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [Command](./01-design-patterns/behavioral/command/) | Gravity-based move validation, win detection, undo history | 50 min | [→](./02-lld-projects/connect-four/) |
| **Rate Limiter** | ⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/) | Token bucket, sliding window, permit scarcity | 60 min | [→](./02-lld-projects/rate-limiter/) |
| **Splitwise** | ⭐⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [Observer](./01-design-patterns/behavioral/observer/) | Expense splitting, Graph | 90 min | [→](./02-lld-projects/splitwise/) |
| **Ride Sharing** | ⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/), [Observer](./01-design-patterns/behavioral/observer/) | Matching, Pricing | 75 min | [→](./02-lld-projects/ride-sharing-system/) |
| **Car Rental** | ⭐⭐⭐ | [Factory](./01-design-patterns/creational/factory-method/), [Strategy](./01-design-patterns/behavioral/strategy/) | Booking, Inventory | 60 min | [→](./02-lld-projects/car-rental/) |
| **Inventory Management** | ⭐⭐⭐ | [Observer](./01-design-patterns/behavioral/observer/), [Strategy](./01-design-patterns/behavioral/strategy/) | Stock invariants, transfer consistency, low-stock alerts | 75 min | [→](./02-lld-projects/inventory-management/) |
| **Job Scheduler** | ⭐⭐⭐⭐ | [State](./01-design-patterns/behavioral/state/), [Strategy](./01-design-patterns/behavioral/strategy/) | Scheduling, retries, idempotency, queue coordination | 90 min | [→](./02-lld-projects/job-scheduler/) |
| **Web Crawler** | ⭐⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/) | Frontier, politeness, deduplication | 90 min | [→](./02-lld-projects/web-crawler/) |
| **Ad Click Aggregator** | ⭐⭐⭐⭐ | [Strategy](./01-design-patterns/behavioral/strategy/) | Event windows, deduplication, aggregation | 90 min | [→](./02-lld-projects/ad-click-aggregator/) |
| **Payment System** | ⭐⭐⭐⭐ | [State](./01-design-patterns/behavioral/state/), [Strategy](./01-design-patterns/behavioral/strategy/) | Payment lifecycle, reconciliation, idempotency | 90 min | [→](./02-lld-projects/payment-system/) |

---

## 📊 Common Complexity Classes

| Complexity | Name | Example Operations |
|------------|------|-------------------|
| O(1) | Constant | Hash table lookup, Array access by index |
| O(log n) | Logarithmic | Binary search, Balanced BST operations |
| O(n) | Linear | Linear search, Single loop iteration |
| O(n log n) | Linearithmic | Merge sort, Heap sort, Quick sort (avg) |
| O(n²) | Quadratic | Nested loops, Bubble sort |
| O(2ⁿ) | Exponential | Recursive Fibonacci, Power set |
| O(n!) | Factorial | Permutations, Traveling salesman (brute) |

### Data Structure Operations

| Structure | Access | Search | Insert | Delete | Notes |
|-----------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | |
| LinkedList | O(n) | O(n) | O(1) | O(1) | |
| HashMap / Hash Table | O(1) | O(1) | O(1) | O(1) | [Advanced Hash Tables](./00-theory/data-structures/advanced-hash-tables.md) |
| TreeMap | O(log n) | O(log n) | O(log n) | O(log n) | |
| Heap | O(1)* | O(n) | O(log n) | O(log n) | |
| Trie | O(1 per node) | O(L) | O(L) | O(L) | |
| Merkle Tree | O(1 root) | O(log n) proof | O(log n) | O(log n) | |

*Heap access is O(1) for min/max only

For tries, `L` is key length. For Merkle trees, search means validating a leaf or range with a proof path rather than arbitrary value lookup.

### Space Complexity Quick Reference

| Structure | Space |
|-----------|-------|
| Variables | O(1) |
| Array of size n | O(n) |
| 2D Matrix n×m | O(n×m) |
| Recursive stack (depth d) | O(d) |
| Hash Map with n entries | O(n) |

---

<a id="system-design-components-map"></a>

## 🗺️ System Design Components Map

### Problem → Components Mapping

| System Type | Key Components Needed |
|-------------|----------------------|
| **URL Shortener** | Hash function, NoSQL DB, Cache, Counter service |
| **Social Feed** | Message queue, Cache, Fan-out service, Timeline DB |
| **Chat App** | WebSockets, Message queue, Presence service |
| **Video Streaming** | CDN, Blob storage, Transcoding service, Adaptive bitrate |
| **E-commerce** | Product catalog, Cart service, Payment gateway, Inventory |
| **Search Engine** | Inverted index, Crawler, Ranking algorithm, Cache |
| **Rate Limiter** | Token bucket/Sliding window, Redis, Distributed counter |
| **Notification** | Message queue, Push service, Preference store |
| **Ride Sharing** | Geolocation, Matching service, Real-time tracking |

### Component Quick Reference

| Component | Purpose | Technologies |
|-----------|---------|--------------|
| **Load Balancer** | Distribute traffic | Nginx, HAProxy, AWS ELB/ALB |
| **Cache** | Reduce latency | Redis, Memcached |
| **Message Queue** | Async processing | Kafka, RabbitMQ, SQS |
| **CDN** | Serve static content globally | CloudFront, Akamai, Cloudflare |
| **DNS** | Name resolution and regional traffic steering | Route53, Cloud DNS, NS1 |
| **SQL Database** | Structured data, ACID | PostgreSQL, MySQL |
| **SQL Fundamentals** | Query shape, joins, transactions, execution plans | PostgreSQL, MySQL |
| **NoSQL Database** | Flexible schema, scale | MongoDB, Cassandra, DynamoDB |
| **Object Storage** | Large files (images, videos) | S3, GCS, Azure Blob |
| **Search Engine** | Full-text search | Elasticsearch, Solr |
| **API Gateway** | Routing, auth, rate limiting | Kong, AWS API Gateway |

### 🎯 Component Quick Decision

```
Need to reduce latency?
└── Caching (Redis), CDN

Need to handle traffic spikes?
└── Load Balancing, Auto-scaling, Message Queues

Need async processing?
└── Message Queues (Kafka, RabbitMQ)

Need to scale database?
├── Read-heavy → Read Replicas
├── Write-heavy → Sharding
└── Both → Sharding + Caching

Need real-time updates?
└── WebSockets, Pub/Sub

Need to prevent abuse?
└── Rate Limiting (Token bucket, Redis)

Need to store large files?
└── Blob Storage (S3) + CDN
```

---

## 🌳 Decision Trees

### Choosing a Database

```
Need to store data?
├── Structured data with relationships?
│   ├── Need ACID transactions? → SQL (PostgreSQL, MySQL)
│   └── Read-heavy, can denormalize? → Consider NoSQL
├── Unstructured/Semi-structured?
│   ├── Document-based? → MongoDB, CouchDB
│   ├── Key-value pairs? → Redis, DynamoDB
│   ├── Wide-column? → Cassandra, HBase
│   └── Graph relationships? → Neo4j, Neptune
└── Large binary files? → Object Storage (S3)
```

### Choosing a Caching Strategy

```
Need caching?
├── What to cache?
│   ├── Database queries → Query result cache
│   ├── API responses → Response cache
│   ├── Sessions → Session store (Redis)
│   └── Static assets → CDN
├── Cache invalidation strategy?
│   ├── Time-based → TTL (Time To Live)
│   ├── Event-based → Write-through/Write-behind
│   └── Manual → Cache aside (lazy loading)
└── Cache location?
    ├── Application level → In-memory (local)
    └── Distributed → Redis, Memcached
```

### Choosing Communication Pattern

```
Services need to communicate?
├── Synchronous needed?
│   ├── Request-Response → REST API, gRPC
│   └── Real-time bidirectional → WebSockets
└── Asynchronous acceptable?
    ├── Fire and forget → Message Queue
    ├── Pub/Sub pattern → Kafka, SNS
    └── Event-driven → Event Bus
```

---

## 🔑 Key Theorems & Concepts

### CAP Theorem
In distributed systems, partition tolerance is assumed. Under partition, you choose consistency-first or availability-first behavior per operation:
- **C**onsistency: All nodes see the same data
- **A**vailability: Every request gets a response
- **P**artition Tolerance: System works despite network failures

| Operation Type | Typical CAP Posture | Example |
|----------------|---------------------|---------|
| Critical writes | Consistency-first | Payment capture, seat/inventory commit |
| Read-heavy browse | Availability-first with bounded staleness | Feed browse, recommendations, catalog reads |
| Mixed workflows | Split by endpoint with explicit contracts | Commerce checkout + product browsing |

Reference packs:
- [CAP Theory Foundations](./00-theory/system-design-fundamentals/cap-theorem.md)
- [CAP Interview Q&A](./03-hld-concepts/cap-theorem/INTERVIEW-QA.md)

### Byzantine Fault Tolerance (BFT) vs Crash-Fault Tolerance (CFT)
Defines the bounds of distributed consensus based on the assumed failure model.
- **CFT**: Nodes may crash but do not lie. Requires $N \ge 2f + 1$ nodes to tolerate $f$ failures. Used in controlled environments (Raft, Paxos).
- **BFT**: Nodes may fail arbitrarily, including malicious collusion. Requires $N \ge 3f + 1$ nodes. Used in public networks (PBFT, HotStuff, Tendermint).

Reference:
- [BFT Theory Foundations](./00-theory/system-design-fundamentals/byzantine-fault-tolerance.md)

### ACID vs BASE

| ACID (SQL) | BASE (NoSQL) |
|------------|--------------|
| Atomicity | Basically Available |
| Consistency | Soft state |
| Isolation | Eventually consistent |
| Durability | |

### Consistency Patterns
- **Strong**: Read always returns latest write (expensive)
- **Eventual**: Given time, all reads return latest (cheap)
- **Causal**: Preserves cause-effect order (middle ground)
- **Logical Clocks & TrueTime**: Overcoming physical clock drift via vector clocks and Spanner commit waits ([Theory](./03-hld-concepts/logical-clocks-truetime/THEORY.md))

### Distributed Consensus & State
- **FLP Impossibility**: Consensus cannot be guaranteed in asynchronous systems with crash failures ([Theory](./00-theory/system-design-fundamentals/flp-impossibility.md))
- **Chandy-Lamport Snapshots**: Global state recording and consistent cuts without freezing the system ([Theory](./00-theory/system-design-fundamentals/distributed-snapshots-chandy-lamport.md))
- **SWIM Protocol**: Decentralized group membership, scalable O(1) failure detection, and infection-style dissemination ([Theory](./00-theory/distributed-systems/swim-gossip-protocol.md))

### Interview Delivery Concepts
- [System Design Interview Delivery Framework](./00-theory/system-design-fundamentals/system-design-interview-delivery-framework.md): Structured 45-60 minute interview execution flow
- [ML Generalization](./06-genai-systems/00-concepts/ml-generalization/README.md): Overfitting/underfitting, drift, and production diagnostics for applied-ML interviews
- [Concurrency in LLD](./00-theory/system-design-fundamentals/concurrency-in-lld.md): Correctness, coordination, and scarcity playbook for class-level design rounds
- [Memory Models & Cache Coherence](./00-theory/system-design-fundamentals/memory-models-and-cache-coherence.md): Hardware memory hierarchy, false sharing, memory models, and non-blocking mechanics
- [LLD Interview Q&A](./02-lld-projects/INTERVIEW-QA.md): Follow-up responses, scoring cues, and extension prompts for class-level rounds
- [LLD Interview Framework Quiz](./quizzes/lld-interview-framework-quiz.md): 25-question self-check covering requirements, modeling, and pitfalls (answers at [./quizzes/answers/lld-interview-framework-answers.md](./quizzes/answers/lld-interview-framework-answers.md))
- [LLD Concepts Flashcards (100 cards)](./flashcards/lld-concepts.md): Question-only deck covering OOP, pattern usage, delivery checkpoints, and new project drills
- [Salary Negotiation Playbook](./resources/interview-tips/salary-negotiation-playbook.md): Offer-stage framework for stakeholder routing, component strategy, and closing discipline
- [Salary Negotiation Quiz](./quizzes/salary-negotiation-quiz.md): 36-question self-check for offer-stage strategy, pitfalls, and adaptation scenarios (answers at [./quizzes/answers/salary-negotiation-answers.md](./quizzes/answers/salary-negotiation-answers.md))
- [Salary Negotiation Flashcards (60 cards)](./flashcards/salary-negotiation.md): Question-only deck for rehearsal of compensation strategy and decision quality
- [Pattern Selection (HLD Concepts)](./03-hld-concepts/pattern-selection/): Fast mapping from bottlenecks to architectural patterns

---

## 📐 Back-of-Envelope Numbers

### Quick Estimates

| Metric | Value | Formula |
|--------|-------|---------|
| Seconds in a day | 86,400 | (~100K for easy math) |
| QPS for 1M daily users | ~12 QPS | 1M / 86,400 |
| QPS for 100M daily users | ~1,200 QPS | 100M / 86,400 |
| Storage for 1M records (1KB each) | ~1 GB | |
| Read:Write ratio (typical) | 100:1 to 1000:1 | |

### Data Size Reference

| Type | Size |
|------|------|
| Character (UTF-8) | 1-4 bytes |
| Integer | 4 bytes |
| Long/Timestamp | 8 bytes |
| UUID | 16 bytes |
| Average URL | 100 bytes |
| Tweet | ~300 bytes |
| Image thumbnail | 10-50 KB |
| Profile picture | 100-500 KB |
| Video (1 min, compressed) | 10-50 MB |

### Latency Numbers (Know These!)

| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 7 ns |
| RAM access | 100 ns |
| SSD random read | 150 μs |
| HDD random read | 10 ms |
| Network (same DC) | 0.5 ms |
| Network (cross-country) | 50-100 ms |
| Network (cross-continent) | 150-300 ms |

### Quick Math

```
1 million requests/day ≈ 12 QPS
1 billion requests/day ≈ 12,000 QPS

1 KB × 1 million = 1 GB
1 MB × 1 million = 1 TB
1 GB × 1 million = 1 PB

Traffic doubles every 18 months (plan for 3x)
```

Use these in context:
- [Performance Numbers Cheatsheet](./00-theory/cheat-sheets/performance-numbers.md)
- [HLD Core Concepts Practice Template](./resources/templates/practice-hld-core-concepts.md)
- [Core Concepts Scaling Judgment Solution](./solutions/hld-core-concepts-scaling-judgment.md)

---

## 🔗 Cross-Reference Guide

### Pattern → Project Mapping

| Pattern | Used In These LLD Projects |
|---------|---------------------------|
| Singleton | [Parking Lot](./02-lld-projects/parking-lot/) (lot instance), [Elevator](./02-lld-projects/elevator-system/) (system) |
| Factory | [Parking Lot](./02-lld-projects/parking-lot/) (vehicles), [Library](./02-lld-projects/library-management/) (books) |
| Strategy | [Parking Lot](./02-lld-projects/parking-lot/) (pricing), [Chess](./02-lld-projects/chess-game/) (piece movement), [Rate Limiter](./02-lld-projects/rate-limiter/) (algorithms) |
| Observer | [Elevator](./02-lld-projects/elevator-system/) (floor buttons), [Library](./02-lld-projects/library-management/) (notifications) |
| State | [Elevator](./02-lld-projects/elevator-system/) (states), [Vending Machine](./02-lld-projects/vending-machine/) (states), [ATM](./02-lld-projects/atm-system/) (transactions) |
| Command | [Chess](./02-lld-projects/chess-game/) (moves), [Stack Overflow](./02-lld-projects/stack-overflow/) (actions) |

### Concept → System Mapping

| HLD Concept | Used In These Systems |
|-------------|----------------------|
| [Caching](./03-hld-concepts/caching/) | [URL Shortener](./04-hld-projects/url-shortener/), [News Feed](./04-hld-projects/news-feed/), [Video Streaming](./04-hld-projects/video-streaming/), [Distributed Cache](./04-hld-projects/distributed-cache/) |
| [Load Balancing](./03-hld-concepts/load-balancing/) | All systems |
| [Database Sharding](./03-hld-concepts/database-sharding/) | [Chat Service](./04-hld-projects/chat-service/), [News Feed](./04-hld-projects/news-feed/) |
| [Data Partitioning](./03-hld-concepts/data-partitioning/) | [URL Shortener](./04-hld-projects/url-shortener/), [Chat Service](./04-hld-projects/chat-service/), [News Feed](./04-hld-projects/news-feed/) |
| [SQL vs NoSQL](./03-hld-concepts/sql-vs-nosql/) | [Chat Service](./04-hld-projects/chat-service/), [News Feed](./04-hld-projects/news-feed/), [Ecommerce Backend](./04-hld-projects/ecommerce-backend/) |
| [SQL Fundamentals](./03-hld-concepts/sql-fundamentals/) | Query-heavy APIs, reporting surfaces, transactional workflow boundaries |
| [MySQL](./03-hld-concepts/mysql/) | Web commerce, catalog metadata, relational account systems, read-replica workloads |
| [Cassandra](./03-hld-concepts/cassandra/) | [News Feed](./04-hld-projects/news-feed/) (write-heavy feeds), timeline/event history storage patterns |
| [DynamoDB](./03-hld-concepts/dynamodb/) | [URL Shortener](./04-hld-projects/url-shortener/) (key-value lookups), metadata/index-driven API workloads |
| [MongoDB](./03-hld-concepts/mongodb/) | Product catalogs, content metadata, user profiles, document-oriented read models |
| [Consistent Hashing](./03-hld-concepts/consistent-hashing/) | [Database Sharding](./03-hld-concepts/database-sharding/), [Distributed Cache](./04-hld-projects/distributed-cache/), collaboration session routing workloads |
| [CAP Theorem](./03-hld-concepts/cap-theorem/) | Multi-region transaction + browse path trade-off design |
| [Message Queues](./03-hld-concepts/message-queues/) | [News Feed](./04-hld-projects/news-feed/) (fan-out), [Notification Service](./04-hld-projects/notification-service/), [Video Streaming](./04-hld-projects/video-streaming/) (transcoding) |
| [DNS](./03-hld-concepts/dns/) | [Video Streaming](./04-hld-projects/video-streaming/), [Ride Sharing](./04-hld-projects/ride-sharing/), globally distributed systems |
| [API Design](./03-hld-concepts/api-design/) | All HLD systems (interface contracts, pagination, idempotency) |
| [WebSockets](./03-hld-concepts/websockets/) | [Chat Service](./04-hld-projects/chat-service/), [Brokerage Platform](./04-hld-projects/brokerage-platform/), [Collaborative Document Editor](./04-hld-projects/collaborative-doc-editor/) |
| [Idempotency](./03-hld-concepts/idempotency/) | [Payment System](./04-hld-projects/payment-system/), [Ad Click Aggregator](./04-hld-projects/ad-click-aggregator/), [Job Scheduler](./04-hld-projects/job-scheduler/), [Web Crawler](./04-hld-projects/web-crawler/), agent tool workflows |
| [Distributed Transactions](./03-hld-concepts/distributed-transactions/) | [Payment System](./04-hld-projects/payment-system/), [E-commerce](./04-hld-projects/ecommerce-backend/), [Ticketing Platform](./04-hld-projects/ticketing-platform/), [Workflow Orchestration](./03-hld-concepts/workflow-orchestration/) |
| [Rate Limiting](./03-hld-concepts/rate-limiting/) | [API Gateway](./03-hld-concepts/api-gateway/), [URL Shortener](./04-hld-projects/url-shortener/) |
| [CDN](./03-hld-concepts/cdn/) | [Video Streaming](./04-hld-projects/video-streaming/), [E-commerce](./04-hld-projects/ecommerce-backend/) |
| [Read Scaling](./03-hld-concepts/read-scaling/) | [Caching](./03-hld-concepts/caching/), [Database Replication](./03-hld-concepts/database-replication/), [CDN](./03-hld-concepts/cdn/), [News Feed](./04-hld-projects/news-feed/), [Video Streaming](./04-hld-projects/video-streaming/) |
| [Write Scaling](./03-hld-concepts/write-scaling/) | [Database Sharding](./03-hld-concepts/database-sharding/), [Message Queues](./03-hld-concepts/message-queues/), [News Feed](./04-hld-projects/news-feed/), [Video Streaming](./04-hld-projects/video-streaming/) |
| [Large Blob Handling](./03-hld-concepts/large-blob-handling/) | [CDN](./03-hld-concepts/cdn/), [Caching](./03-hld-concepts/caching/), [File Storage](./04-hld-projects/file-storage/), [Video Streaming](./04-hld-projects/video-streaming/) |
| [Long-Running Tasks](./03-hld-concepts/long-running-tasks/) | [Message Queues](./03-hld-concepts/message-queues/), [Workflow Orchestration](./03-hld-concepts/workflow-orchestration/), [File Storage](./04-hld-projects/file-storage/), [Video Streaming](./04-hld-projects/video-streaming/) |
| [Real-time Updates](./03-hld-concepts/real-time-updates/) | [Chat Service](./04-hld-projects/chat-service/), [Notification Service](./04-hld-projects/notification-service/), [News Feed](./04-hld-projects/news-feed/), [Ride Sharing](./04-hld-projects/ride-sharing/), [Collaborative Document Editor](./04-hld-projects/collaborative-doc-editor/) |
| [Contention Control](./03-hld-concepts/contention-control/) | [E-commerce](./04-hld-projects/ecommerce-backend/), [Ride Sharing](./04-hld-projects/ride-sharing/), [URL Shortener](./04-hld-projects/url-shortener/) |
| [Workflow Orchestration](./03-hld-concepts/workflow-orchestration/) | [E-commerce](./04-hld-projects/ecommerce-backend/), [Video Streaming](./04-hld-projects/video-streaming/), [File Storage](./04-hld-projects/file-storage/), [Brokerage Platform](./04-hld-projects/brokerage-platform/) |
| [Monitoring & Observability](./03-hld-concepts/monitoring-observability/) | [Content Moderation Platform](./04-hld-projects/content-moderation-platform/), [Bot Detection Platform](./04-hld-projects/bot-detection-platform/), [Video Streaming](./04-hld-projects/video-streaming/) |
| [Distributed Consensus Raft](./03-hld-concepts/distributed-consensus-raft/) | [Database Replication](./03-hld-concepts/database-replication/), [ZooKeeper](./03-hld-concepts/zookeeper/) |

### When Studying... Also Review...

| Topic | Related Topics |
|-------|---------------|
| [Networking Essentials](./00-theory/networking-basics/networking-essentials.md) | [Load Balancing](./03-hld-concepts/load-balancing/), [DNS](./03-hld-concepts/dns/), [Service Discovery](./03-hld-concepts/service-discovery/) |
| [REST API Design](./00-theory/networking-basics/rest-api-design.md) | [API Design](./03-hld-concepts/api-design/), [API Gateway](./03-hld-concepts/api-gateway/), [Rate Limiting](./03-hld-concepts/rate-limiting/) |
| [Data Modeling](./00-theory/database-concepts/data-modeling.md) | [SQL Fundamentals](./03-hld-concepts/sql-fundamentals/), [Database Sharding](./03-hld-concepts/database-sharding/), [MySQL](./03-hld-concepts/mysql/), [MongoDB](./03-hld-concepts/mongodb/), [Cassandra](./03-hld-concepts/cassandra/), [DynamoDB](./03-hld-concepts/dynamodb/), [News Feed](./04-hld-projects/news-feed/) |
| [Concurrency in LLD](./00-theory/system-design-fundamentals/concurrency-in-lld.md) | [Movie Ticket Booking](./02-lld-projects/movie-ticket-booking/), [Rate Limiter](./02-lld-projects/rate-limiter/), [Job Scheduler](./02-lld-projects/job-scheduler/) |
| [Indexing](./00-theory/database-concepts/indexing.md) | [Elasticsearch](./03-hld-concepts/elasticsearch/), [Caching](./03-hld-concepts/caching/), [E-commerce](./04-hld-projects/ecommerce-backend/) |
| [Trie](./00-theory/big-data-structures/trie.md) | [Trie Coding Pack](./05-coding-problems/trie/README.md), autocomplete, route matching, prefix search |
| [Merkle Tree](./00-theory/big-data-structures/merkle-tree.md) | replicated storage repair, audit trails, tamper-evident synchronization |
| [Singleton Pattern](./01-design-patterns/creational/singleton/) | Database connection pools, [Caching](./03-hld-concepts/caching/) |
| [Factory Pattern](./01-design-patterns/creational/factory-method/) | Plugin architectures, LLD vehicle/user creation |
| [Observer Pattern](./01-design-patterns/behavioral/observer/) | Event-driven systems, [Message Queues](./03-hld-concepts/message-queues/) |
| [Strategy Pattern](./01-design-patterns/behavioral/strategy/) | Payment systems, [Parking Lot pricing](./02-lld-projects/parking-lot/) |
| [State Pattern](./01-design-patterns/behavioral/state/) | [Vending Machine](./02-lld-projects/vending-machine/), [ATM System](./02-lld-projects/atm-system/) |
| [Caching](./03-hld-concepts/caching/) | [Flyweight pattern](./01-design-patterns/structural/flyweight/), [Proxy pattern](./01-design-patterns/structural/proxy/) |
| [Message Queues](./03-hld-concepts/message-queues/) | [Command pattern](./01-design-patterns/behavioral/command/) |
| [Load Balancing](./03-hld-concepts/load-balancing/) | [Consistent Hashing](./03-hld-concepts/consistent-hashing/) |

---

## 📊 HLD Systems Comparison

| System | Scale | Key Challenges | Concepts Used | Est. Time | Link |
|--------|-------|----------------|---------------|-----------|------|
| URL Shortener | 100M+ URLs | Encoding, Collision | Hashing, Cache, NoSQL | 45 min | [→](./04-hld-projects/url-shortener/) |
| News Feed | 500M users | Celebrity problem | Fan-out, Timeline, Cache | 60 min | [→](./04-hld-projects/news-feed/) |
| Chat (WhatsApp) | 2B users | Real-time, Delivery | WebSockets, Queues, Presence | 60 min | [→](./04-hld-projects/chat-service/) |
| Video Streaming | 1B views/day | Storage, Streaming | CDN, Transcoding, Adaptive | 75 min | [→](./04-hld-projects/video-streaming/) |
| Ride Sharing | 50M riders | Matching, Geospatial, Lifecycle consistency | Geo indexing, real-time updates, contention control | 75 min | [→](./04-hld-projects/ride-sharing/) |
| Job Scheduler | 10K+ jobs/sec | Jitter bounds, retry safety, leases | Long-running tasks, queues, workflow orchestration, idempotency | 60 min | [→](./04-hld-projects/job-scheduler/) |
| Web Crawler | 10B pages target | Frontier fairness, politeness, dedupe | DNS, queues, write scaling, idempotency | 75 min | [→](./04-hld-projects/web-crawler/) |
| Ad Click Aggregator | 10K clicks/sec peak | Idempotent counting, late events, reconciliation | Kafka/Flink patterns, write scaling, idempotency | 75 min | [→](./04-hld-projects/ad-click-aggregator/) |
| Payment System | 10K+ TPS | Financial integrity, async gateways, auditability | Distributed transactions, workflow orchestration, idempotency, observability | 75 min | [→](./04-hld-projects/payment-system/) |
| Metrics Monitoring | 5M metrics/sec | Cardinality, alert latency, query windows | Time-series, monitoring/observability, scaling reads/writes | 75 min | [→](./04-hld-projects/metrics-monitoring/) |
| Realtime Metrics Platform | 3M points/sec peak | Event-time correctness, replay safety | Stream processing, TSDB, retention tiers | 75 min | [→](./04-hld-projects/realtime-metrics-platform/) |
| Brokerage Platform | 20M users | Realtime quotes + strong order consistency | WebSockets, workflow orchestration, reconciliation | 75 min | [→](./04-hld-projects/brokerage-platform/) |
| Collaborative Document Editor | Millions of sessions | Concurrent edits, convergence, replay | WebSockets, consistent hashing, long-running tasks | 75 min | [→](./04-hld-projects/collaborative-doc-editor/) |
| Distributed Cache | 100K+ req/s | Key distribution, hot keys, failover | Consistent hashing, replication, caching | 60 min | [→](./04-hld-projects/distributed-cache/) |
| E-commerce | 100M products | Inventory, Search | Distributed transactions, catalog, cart, payment | 75 min | [→](./04-hld-projects/ecommerce-backend/) |
| Notification Service | 1B notifs/day | Multi-channel, Scale | Queues, Templates, Priority | 60 min | [→](./04-hld-projects/notification-service/) |
| Content Moderation Platform | 1B posts/day | precision guardrails, class imbalance, review queue | Monitoring, queues, policy engine | 75 min | [→](./04-hld-projects/content-moderation-platform/) |
| Bot Detection Platform | 500M+ DAU | adversarial adaptation, sparse labels, false-positive control | Streaming signals, rate limiting, observability | 75 min | [→](./04-hld-projects/bot-detection-platform/) |
| Video Recommendations | 1B views/day class | multi-stage ranking, exploration, delayed feedback loops | Read scaling, monitoring, ranking pipelines | 75 min | [→](./04-hld-projects/video-recommendations/) |

---

## 🤖 Generative AI System Design

> Modern interviews increasingly feature GenAI prompts. This section covers the key concepts and trade-offs you need. See [06-genai-systems](./06-genai-systems/) for full coverage.

### GenAI Concepts at a Glance

| Concept | One-Liner | Classical Tie-in | Link |
|---------|-----------|------------------|------|
| **RAG Architecture** | Augment LLM answers with retrieved documents | Caching, Message Queues | [→](./06-genai-systems/00-concepts/rag-architecture/) |
| **LLM-Oriented System Design** | Apply classical HLD framing to LLM systems (tokens, context windows, routing) | Load Balancing, Caching | [→](./06-genai-systems/00-concepts/llm-system-design/) |
| **Prompting, Tools & Agents** | Compose prompts, tool calls, and agent loops safely | API Gateway, Message Queues | [→](./06-genai-systems/00-concepts/prompting-tools-agents/) |
| **Vector Databases** | Store and query embeddings for similarity search | Database Sharding | [→](./06-genai-systems/00-concepts/vector-databases/) |
| **LLM Safety & Guardrails** | Filter harmful inputs/outputs, mitigate hallucinations | Rate Limiting | [→](./06-genai-systems/00-concepts/safety-governance/) |
| **Evaluation Frameworks** | Measure quality, faithfulness, and relevance | — | [→](./06-genai-systems/00-concepts/llm-evaluation/) |
| **Model Generalization** | Diagnose overfit/underfit and production drift with slice-aware analysis | Monitoring & Observability | [→](./06-genai-systems/00-concepts/ml-generalization/) |
| **Safety, Eval & Governance** | Attack surfaces, taxonomies, risk categories, ASR, benchmarks | Monitoring & Observability | [→](./06-genai-systems/00-concepts/safety-eval/) |
| **Model Routing & Orchestration** | Route requests to optimal model by cost/quality/latency | Load Balancing | [→](./06-genai-systems/00-concepts/model-routing-orchestration/) |
| **Token / Cost / Latency** | Manage token budgets, estimate costs, optimize latency | — | [→](./06-genai-systems/00-concepts/token-cost-latency/) |
| **Streaming & KV-Cache** | Token-by-token delivery and cache optimization | Caching, CDN | [→](./06-genai-systems/00-concepts/streaming-kv-cache/) |
| **GenAI Design Patterns** | Recurring architecture patterns (RAG, Agent Loop, Guardrail Sandwich, Router) | Design Patterns | [→](./06-genai-systems/00-concepts/genai-design-patterns/) |

Twelve GenAI concepts are now indexed here, including model generalization.

> 📋 **New:** Use the [GenAI SD Framework](./06-genai-systems/GENAI-SD-FRAMEWORK.md) for a reusable 6-step interview approach. See also [Classic vs GenAI Comparison](./06-genai-systems/CLASSIC-VS-GENAI.md) and [Top 10 Pitfalls](./06-genai-systems/PITFALLS.md).

### 🎯 GenAI Quick Decision

```
Designing an LLM-powered system?
├── Need domain-specific knowledge?
│   ├── Corpus changes frequently? → RAG
│   ├── Narrow, stable domain? → Fine-tuning
│   └── Both? → RAG + fine-tuned model
├── Need multi-step reasoning?
│   └── Agentic workflow with tool routing
├── Need safety & compliance?
│   └── Input/output guardrails + evaluation harness
├── Need low latency?
│   ├── Streaming + KV-Cache
│   └── Smaller model or model routing
└── Need to control costs?
    └── Token budgeting + semantic caching + model cascading
```

### GenAI Component → System Mapping

| Component | Used In These GenAI Systems |
|-----------|-----------------------------|
| Document Chunker | RAG Enterprise Search, Content Moderation |
| Embedding Service | RAG Enterprise Search, AI Copilot |
| Vector Retriever | RAG Enterprise Search, Conversational Chatbot |
| Prompt Builder | All GenAI systems |
| Safety Filter | Conversational Chatbot, Content Moderation, LLM Safety & Eval Platform |
| Tool Router | AI Copilot, Agentic Workflow |
| Conversation Memory | Conversational Chatbot |
| Evaluation Harness | All GenAI systems (observability), LLM Safety & Eval Platform |

### When Studying GenAI... Also Review...

| GenAI Topic | Related Classical Topics |
|-------------|------------------------|
| RAG Architecture | [Caching](./03-hld-concepts/caching/), [Message Queues](./03-hld-concepts/message-queues/) |
| Vector Databases | [Database Sharding](./03-hld-concepts/database-sharding/), [Consistent Hashing](./03-hld-concepts/consistent-hashing/) |
| Model Routing | [Load Balancing](./03-hld-concepts/load-balancing/), [Strategy Pattern](./01-design-patterns/behavioral/strategy/) |
| Safety Filters | [Chain of Responsibility](./01-design-patterns/behavioral/chain-of-responsibility/), [Rate Limiting](./03-hld-concepts/rate-limiting/) |
| Safety, Eval & Governance | [Monitoring & Observability](./03-hld-concepts/monitoring-observability/), [Rate Limiting](./03-hld-concepts/rate-limiting/) |
| Token / Cost / Latency | [Rate Limiting](./03-hld-concepts/rate-limiting/), [Caching](./03-hld-concepts/caching/) |
| GenAI Design Patterns | [Design Patterns](./01-design-patterns/), [HLD Concepts](./03-hld-concepts/) |
| Streaming | [Observer Pattern](./01-design-patterns/behavioral/observer/), [CDN](./03-hld-concepts/cdn/) |

---

<p align="center">
  <b>Bookmark this page for quick reference during study! 📌</b>
</p>

---

## Source Set 13-18 Coverage Update (March 2026)

- Added practical integration notes for contention control, real-time updates, social search indexing, write scaling, and workflow orchestration.
- Added cross-links to new HLD projects: online auction, live comments, social post search, and price tracking service.
