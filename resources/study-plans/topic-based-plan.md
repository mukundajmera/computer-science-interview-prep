# 🎯 Topic-Based Learning Paths

Targeted learning paths organized by concept. Choose based on your weak areas or specific goals.

---

## 📋 Available Learning Paths

| Path | Duration | Best For |
|------|----------|----------|
| 🎨 [Design Patterns Deep Dive](#-design-patterns-deep-dive) | 5-7 days | Weak in pattern recognition |
| 🏗️ [LLD Mastery](#️-lld-mastery) | 5-7 days | Weak in class design |
| ☁️ [HLD Fundamentals](#️-hld-fundamentals) | 5-7 days | Weak in system design |
| 🧠 [Behavioral Interview Track](#-behavioral-interview-track) | 4-5 days | Weak in behavioral signal clarity |
| 🗃️ [Database & Storage](#️-database--storage-path) | 3-4 days | Weak in data modeling |
| 🔄 [Caching Deep Dive](#-caching-deep-dive) | 2-3 days | Need to master caching |
| 🧵 [Concurrency & Scalability](#-concurrency--scalability) | 3-4 days | Weak in distributed systems |

---

## 🎨 Design Patterns Deep Dive

**Duration:** 5-7 days  
**Prerequisites:** Basic OOP understanding  
**Goal:** Recognize and apply the right pattern for any problem

### Day 1: Creational Patterns Foundation

| Time | Topic | Practice |
|------|-------|----------|
| 1 hr | **Singleton** | Implement thread-safe Singleton |
| 1 hr | **Factory Method** | Create a VehicleFactory |
| 1 hr | **Abstract Factory** | Cross-platform UI factory |
| 1 hr | **Builder** | Build a complex User object |
| 30 min | **Prototype** | Clone configuration objects |

**Resources:**
- [01-design-patterns/creational/](../../01-design-patterns/creational/)
- [CONCEPTS.md - Creational Patterns](../../CONCEPTS.md#creational-patterns)

**End of Day Check:**
- [ ] Can explain when to use each pattern
- [ ] Implemented all 5 patterns

---

### Day 2: Structural Patterns

| Time | Topic | Practice |
|------|-------|----------|
| 45 min | **Adapter** | Adapt legacy payment interface |
| 45 min | **Bridge** | Separate remote control from devices |
| 45 min | **Composite** | Build a file system |
| 45 min | **Decorator** | Coffee shop with toppings |
| 30 min | **Facade** | Simplify complex subsystem |
| 30 min | **Flyweight** | Optimize character rendering |
| 30 min | **Proxy** | Lazy loading images |

**Resources:**
- [01-design-patterns/structural/](../../01-design-patterns/structural/)

**End of Day Check:**
- [ ] Can differentiate Adapter vs Bridge vs Decorator
- [ ] Know when Facade vs Adapter is appropriate

---

### Day 3: Behavioral Patterns (Core)

| Time | Topic | Practice |
|------|-------|----------|
| 1 hr | **Observer** | Notification system (push/pull) |
| 1 hr | **Strategy** | Payment processing system |
| 1 hr | **State** | Vending machine states |
| 1 hr | **Command** | Undo/redo text editor |

**Resources:**
- [01-design-patterns/behavioral/](../../01-design-patterns/behavioral/)

**End of Day Check:**
- [ ] Can explain Strategy vs State difference
- [ ] Implemented Observer with both push and pull

---

### Day 4: Behavioral Patterns (Advanced)

| Time | Topic | Practice |
|------|-------|----------|
| 45 min | **Chain of Responsibility** | Request processing pipeline |
| 45 min | **Template Method** | Document generator framework |
| 45 min | **Mediator** | Chat room implementation |
| 45 min | **Memento** | Save/restore game state |
| 30 min | **Iterator** | Custom collection traversal |
| 30 min | **Visitor** | Report generation on objects |

**End of Day Check:**
- [ ] Understand all 11 behavioral patterns
- [ ] Can identify patterns in real frameworks

---

### Day 5: Pattern Recognition & Application

| Time | Activity |
|------|----------|
| 1 hr | **Pattern Decision Tree** - Create your own |
| 2 hrs | **Apply to LLD** - Design Parking Lot using patterns |
| 1 hr | **Pattern Quiz** - Given scenario, choose pattern |

**Pattern Decision Scenarios:**
- "Need exactly one instance" → Singleton
- "Create objects without specifying class" → Factory
- "Add behavior without modifying class" → Decorator
- "Objects need to react to state changes" → Observer
- "Swap algorithms at runtime" → Strategy
- "Object behavior changes with state" → State

**Resources:**
- [resources/cheatsheets/pattern-decision-tree.md](../cheatsheets/pattern-decision-tree.md)

---

### Days 6-7: Integration & Practice

| Day | Activity |
|-----|----------|
| Day 6 | Design 2 LLD problems, consciously apply patterns |
| Day 7 | Review, create personal pattern cheatsheet |

**Recommended LLD Problems:**
- [02-lld-projects/elevator-system/](../../02-lld-projects/elevator-system/) (State pattern)
- [02-lld-projects/vending-machine/](../../02-lld-projects/vending-machine/) (State pattern)
- [02-lld-projects/parking-lot/](../../02-lld-projects/parking-lot/) (Factory, Strategy)

---

## 🏗️ LLD Mastery

**Duration:** 5-7 days  
**Prerequisites:** OOP basics, some pattern knowledge  
**Goal:** Design any LLD problem systematically in 45 minutes

### Day 1: LLD Framework & Foundation

| Time | Topic | Resources |
|------|-------|-----------|
| 1 hr | **7-Step LLD Framework** | [HOW-TO-APPROACH.md](../../02-lld-projects/HOW-TO-APPROACH.md) |
| 1 hr | **Entity Identification** | Practice with 5 problems |
| 1 hr | **Relationship Mapping** | Composition vs Aggregation |
| 1 hr | **LLD Template** | [lld-template.md](../templates/lld-template.md) |

**Practice:**
- [ ] Identify entities for: Library, Hospital, Banking
- [ ] Map relationships for each

---

### Day 2: Pattern Application in LLD

| Time | Topic |
|------|-------|
| 2 hrs | **When to use which pattern in LLD** |
| 2 hrs | **Common pattern combinations** |

**Common LLD Pattern Usage:**

| Problem Type | Patterns |
|--------------|----------|
| Object creation | Factory, Builder |
| State machines | State |
| Pricing/Algorithms | Strategy |
| Notifications | Observer |
| Access control | Proxy |
| Feature extensions | Decorator |

---

### Day 3-4: Core LLD Projects

| Day | Projects | Time Each |
|-----|----------|-----------|
| Day 3 | Parking Lot, LRU Cache | 2 hrs each |
| Day 4 | Elevator, Library Management | 2 hrs each |

**For each project:**
1. Requirements clarification (5 min)
2. Entity identification (5 min)
3. Relationship mapping (5 min)
4. Pattern selection (5 min)
5. Class design (15 min)
6. Edge cases (5 min)
7. Code key classes (15 min)

**Resources:**
- [02-lld-projects/](../../02-lld-projects/)

---

### Day 5-6: Advanced LLD Projects

| Day | Projects | Focus |
|-----|----------|-------|
| Day 5 | Chess Game, Vending Machine | Complex state, Piece hierarchy |
| Day 6 | Hotel Booking, Movie Ticket | Concurrency, Reservations |

---

### Day 7: Mock Practice & Review

| Time | Activity |
|------|----------|
| 1.5 hrs | Mock LLD #1 (45 min + review) |
| 1.5 hrs | Mock LLD #2 (45 min + review) |
| 1 hr | Create personal LLD checklist |

**Self-Assessment Questions:**
- [ ] Did I clarify requirements first?
- [ ] Did I identify all core entities?
- [ ] Did I apply appropriate patterns?
- [ ] Did I handle edge cases?
- [ ] Did I stay within time limit?

---

## ☁️ HLD Fundamentals

**Duration:** 5-7 days  
**Prerequisites:** Basic web architecture understanding  
**Goal:** Design any distributed system with proper trade-off discussions

### Day 1: Core Components

| Time | Topic | Key Points |
|------|-------|------------|
| 1 hr | **Load Balancing** | L4 vs L7, algorithms, health checks |
| 1.5 hrs | **Caching** | Strategies, eviction, invalidation |
| 1 hr | **CDN** | Edge caching, cache headers |
| 30 min | **API Gateway** | Routing, auth, rate limiting |

**Resources:**
- [CONCEPTS.md - Components](../../CONCEPTS.md#component-quick-reference)

---

### Day 2: Database Concepts

| Time | Topic | Key Points |
|------|-------|------------|
| 1 hr | **SQL vs NoSQL** | When to use each |
| 1 hr | **Sharding** | Strategies, consistent hashing, migration triggers |
| 1 hr | **Replication** | Master-slave, sync vs async |
| 1 hr | **CAP Theorem** | Endpoint-level CP/AP choices, degraded mode, reconciliation |

**Resources:**
- [cap-theorem.md](../../00-theory/system-design-fundamentals/cap-theorem.md)
- [CONCEPTS.md - Decision Trees](../../CONCEPTS.md#choosing-a-database)
- [03-hld-concepts/cap-theorem/THEORY.md](../../03-hld-concepts/cap-theorem/THEORY.md)
- [03-hld-concepts/database-sharding/THEORY.md](../../03-hld-concepts/database-sharding/THEORY.md)
- [03-hld-concepts/consistent-hashing/THEORY.md](../../03-hld-concepts/consistent-hashing/THEORY.md)

---

### Day 3: Async Processing & Communication

| Time | Topic | Key Points |
|------|-------|------------|
| 1.5 hrs | **Message Queues** | Kafka, RabbitMQ, ordering |
| 1 hr | **Pub/Sub** | Fan-out, topics |
| 1 hr | **WebSockets** | Real-time bidirectional |
| 30 min | **gRPC vs REST** | When to use each |

---

### Day 4: HLD Framework + First System

| Time | Topic | Resources |
|------|-------|-----------|
| 30 min | **HLD Template** | [DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md) |
| 30 min | **Estimation Practice** | [back-of-envelope.md](../../00-theory/system-design-fundamentals/back-of-envelope.md) |
| 3 hrs | **Design: URL Shortener** | End-to-end design |

---

### Day 5-6: Core HLD Systems

| Day | System | Key Concepts |
|-----|--------|--------------|
| Day 5 | Twitter Feed | Fan-out, timeline caching |
| Day 6 | Chat Application | WebSockets, presence, ordering |

---

### Day 7: Practice & Review

| Time | Activity |
|------|----------|
| 2 hrs | Mock HLD #1 + [practice-hld-core-concepts.md](../templates/practice-hld-core-concepts.md) drill |
| 2 hrs | Mock HLD #2 |
| 1 hr | Create component selection guide + run [hld-concepts-quiz.md](../../quizzes/hld-concepts-quiz.md) |

---

## 🗃️ Database & Storage Path

**Duration:** 3-4 days  
**Prerequisites:** Basic SQL knowledge  
**Goal:** Make optimal database decisions for any system

### Day 1: SQL Deep Dive

| Time | Topic |
|------|-------|
| 1 hr | ACID properties in depth |
| 1 hr | Normalization (1NF to 3NF) |
| 1 hr | Indexing strategies |
| 1 hr | Query optimization |

**Practice:**
- Design schema for e-commerce (Products, Orders, Users)
- Identify indexes needed for common queries

---

### Day 2: NoSQL Deep Dive

| Time | Topic |
|------|-------|
| 1 hr | Document stores (MongoDB) |
| 1 hr | Key-value stores (Redis, DynamoDB) |
| 1 hr | Wide-column stores (Cassandra) |
| 1 hr | Graph databases (Neo4j) |

**Practice:**
- Design schema for social network (NoSQL)
- Design schema for IoT data (Time-series)

---

### Day 3: Scaling Databases

| Time | Topic |
|------|-------|
| 1.5 hrs | Sharding strategies |
| 1 hr | Consistent hashing |
| 1.5 hrs | Replication patterns |
| 1 hr | CAP theorem applications |

**Practice:**
- Design sharding strategy for user data
- Design replication for high availability

---

### Day 4: Integration

| Time | Activity |
|------|----------|
| 2 hrs | Apply to URL Shortener |
| 2 hrs | Apply to Chat Application |
| 1 hr | Create database decision tree |

---

## 🔄 Caching Deep Dive

**Duration:** 2-3 days  
**Prerequisites:** Basic HLD knowledge  
**Goal:** Master caching for any system

### Day 1: Caching Fundamentals

| Time | Topic |
|------|-------|
| 1 hr | Cache-aside pattern |
| 1 hr | Write-through, Write-behind |
| 1 hr | Eviction policies (LRU, LFU, TTL) |
| 1 hr | Cache invalidation strategies |

**Resources:**
- [CONCEPTS.md - Caching](../../CONCEPTS.md#choosing-a-caching-strategy)
- [02-lld-projects/lru-cache/](../../02-lld-projects/lru-cache/)

---

### Day 2: Distributed Caching

| Time | Topic |
|------|-------|
| 1.5 hrs | Redis architecture |
| 1 hr | Memcached vs Redis |
| 1 hr | CDN caching |
| 30 min | Cache stampede prevention |

---

### Day 3: Application

| Time | Activity |
|------|----------|
| 1.5 hrs | Design caching for Twitter Feed |
| 1.5 hrs | Design caching for E-commerce |
| 1 hr | Create caching decision checklist |

---

## 🧵 Concurrency & Scalability

**Duration:** 3-4 days  
**Prerequisites:** Basic threading knowledge  
**Goal:** Design thread-safe and scalable systems

### Day 1: Concurrency Fundamentals

| Time | Topic |
|------|-------|
| 1 hr | Thread safety basics |
| 1 hr | Locks, mutexes, semaphores |
| 1 hr | Deadlock prevention |
| 1 hr | Concurrent data structures |

---

### Day 2: LLD Concurrency

| Time | Topic |
|------|-------|
| 2 hrs | Thread-safe Singleton |
| 2 hrs | Concurrent booking (seats, rooms) |
| 1 hr | Producer-consumer pattern |

**Practice:**
- [02-lld-projects/movie-ticket-booking/](../../02-lld-projects/movie-ticket-booking/)
- [02-lld-projects/hotel-reservation/](../../02-lld-projects/hotel-reservation/)

---

### Day 3: Distributed Systems

| Time | Topic |
|------|-------|
| 1.5 hrs | Horizontal scaling |
| 1 hr | Stateless services |
| 1.5 hrs | Distributed locking |
| 1 hr | Eventual consistency |

---

### Day 4: Application

| Time | Activity |
|------|----------|
| 2 hrs | Design Rate Limiter (distributed) |
| 2 hrs | Design Notification System |
| 1 hr | Scalability checklist |

---

## 🧠 Behavioral Interview Track

**Duration:** 4-5 days  
**Prerequisites:** Story catalog from your recent projects  
**Goal:** Deliver high-signal behavioral answers for IC and manager variants

### Day 1: Big Three Story Architecture

| Time | Topic | Practice |
|------|-------|----------|
| 1 hr | TMAY structure | Build 60-90 second role-fit summary |
| 1.5 hrs | Favorite project | Add constraints, trade-offs, and outcomes |
| 1.5 hrs | Conflict story | Build professional resolution narrative |
| 1 hr | Follow-up prep | Drill ownership and reflection probes |

**Resources:**
- [behavioral-big-three.md](../interview-tips/behavioral-big-three.md)
- [behavioral-story-template.md](../templates/behavioral-story-template.md)

### Day 2: Calibration and Audience Adaptation

| Time | Topic |
|------|-------|
| 1.5 hrs | Big-tech scale and rubric calibration |
| 1 hr | IC vs manager story variants |
| 1.5 hrs | Special round adaptation (recruiter, leadership, cross-functional) |
| 1 hr | Tailored closes and follow-up invites |

**Resources:**
- [behavioral-big-tech-calibration.md](../interview-tips/behavioral-big-tech-calibration.md)
- [behavioral-special-interview-types.md](../interview-tips/behavioral-special-interview-types.md)

### Day 3: Pressure Practice

| Time | Activity |
|------|----------|
| 1 hr | Solo recording + review |
| 1 hr | AI drill with interruption/pivot prompts |
| 1.5 hrs | Peer mock with scorecard |
| 1 hr | Targeted re-drill of weakest signals |

**Resources:**
- [behavioral-practice-roadmap.md](../interview-tips/behavioral-practice-roadmap.md)
- [behavioral-interviews-quiz.md](../../quizzes/behavioral-interviews-quiz.md)

### Day 4-5: Mock Loop Simulation

| Day | Activity |
|-----|----------|
| Day 4 | 2 behavioral mock rounds (IC + manager variants) |
| Day 5 | Debrief, pitfall cleanup, and final timed run |

**Pitfall prevention:**
- [behavioral-pitfalls.md](../interview-tips/behavioral-pitfalls.md)
- [common-pitfalls.md](../interview-tips/common-pitfalls.md)

---

## 📊 Path Combinations

Choose paths based on your interview type:

| Interview Focus | Recommended Paths |
|-----------------|-------------------|
| LLD Only | Design Patterns → LLD Mastery |
| HLD Only | HLD Fundamentals → Caching → Database |
| Behavioral-heavy Loop | Behavioral Interview Track → 2 targeted mocks |
| Mixed LLD/HLD | Design Patterns → LLD (3 days) → HLD (5 days) |
| Specific Weakness | Start with weakest area path |

---

## ✅ Path Completion Checklist

Track which paths you've completed:

```markdown
## My Learning Path Progress

### Design Patterns Deep Dive
- [ ] Day 1: Creational Patterns
- [ ] Day 2: Structural Patterns
- [ ] Day 3: Behavioral (Core)
- [ ] Day 4: Behavioral (Advanced)
- [ ] Day 5: Pattern Recognition
- [ ] Days 6-7: Integration

### LLD Mastery
- [ ] Day 1: Framework
- [ ] Day 2: Pattern Application
- [ ] Days 3-4: Core Projects
- [ ] Days 5-6: Advanced Projects
- [ ] Day 7: Mock Practice

### HLD Fundamentals
- [ ] Day 1: Core Components
- [ ] Day 2: Database Concepts
- [ ] Day 3: Async Processing
- [ ] Day 4: First System
- [ ] Days 5-6: Core Systems
- [ ] Day 7: Practice

### Behavioral Interview Track
- [ ] Day 1: Big Three architecture
- [ ] Day 2: Calibration and adaptation
- [ ] Day 3: Pressure practice
- [ ] Days 4-5: Mock loop simulation

[Continue for other paths...]
```

---

## 🔗 Cross-Path Connections

| Topic in Path A | Related Topic in Path B |
|-----------------|-------------------------|
| Observer Pattern | Pub/Sub in HLD |
| Strategy Pattern | Algorithm selection in systems |
| LRU Cache (LLD) | Caching in HLD |
| State Pattern | State machines in distributed systems |
| Factory Pattern | Service instantiation |

---

*Choose your path and start learning! 🚀*

---

## Additional Topic Mapping (March 2026)

- Contention-heavy systems: online auction.
- Real-time fanout systems: live comments.
- Search-heavy systems: social post search.
- Event aggregation systems: YouTube Top-K variant.
- Source 24-28 set:
  - Scheduler reliability: `job-scheduler`
  - Crawl + frontier systems: `web-crawler`
  - Stream aggregation correctness: `ad-click-aggregator`
  - Financial correctness and idempotency: `payment-system`
  - Monitoring baseline: `metrics-monitoring`
