# 📚 1-Month Deep Dive Study Plan

A comprehensive 4-week plan for thorough system design interview preparation.

---

## 📋 Overview

| Week | Focus Area | Hours/Week | Topics |
|------|------------|------------|--------|
| 1 | Foundations + Design Patterns | 20-25 hrs | OOP, SOLID, All Design Patterns |
| 2 | LLD Projects | 20-25 hrs | 10 LLD Projects, Pattern Application |
| 3 | HLD Concepts + Systems | 25-30 hrs | Core Concepts, 4 System Designs |
| 4 | Advanced Systems + Mock Practice | 20-25 hrs | 4 More Systems, Mock Interviews, Review |

**Total Time:** ~90-105 hours over 4 weeks

---

## 📅 Week 1: Foundations + Design Patterns

**Goal:** Build a solid foundation in OOP principles and master all design patterns.

### Day 1 (Monday): OOP Principles & SOLID

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **OOP Principles** | [00-theory/oop-principles/](../../00-theory/oop-principles/) |
| | - Encapsulation | [encapsulation-abstraction.md](../../00-theory/oop-principles/encapsulation-abstraction.md) |
| | - Abstraction | |
| | - Inheritance | |
| | - Polymorphism | |
| 2 hrs | **SOLID Principles** | [solid-principles.md](../../00-theory/oop-principles/solid-principles.md) |
| | - Single Responsibility | |
| | - Open/Closed | |
| | - Liskov Substitution | |
| | - Interface Segregation | |
| | - Dependency Inversion | |

**Practice:**
- [ ] Write examples violating each SOLID principle
- [ ] Refactor to follow the principle
- [ ] Identify SOLID violations in existing code

---

### Day 2 (Tuesday): Complexity Analysis

| Time | Topic | Resources |
|------|-------|-----------|
| 1 hr | **Big-O Notation** | [00-theory/complexity-analysis/big-o-notation.md](../../00-theory/complexity-analysis/big-o-notation.md) |
| | - Time complexity | |
| | - Space complexity | |
| | - Best/Average/Worst case | |
| 1 hr | **Common Complexities** | [common-complexities.md](../../00-theory/complexity-analysis/common-complexities.md) |
| | - Data structure operations | |
| | - Sorting algorithms | |
| | - Searching algorithms | |

**Practice:**
- [ ] Analyze complexity of 10 code snippets
- [ ] Compare data structures by complexity
- [ ] Practice back-of-envelope calculations

---

### Day 3 (Wednesday): Database Fundamentals

| Time | Topic | Resources |
|------|-------|-----------|
| 1 hr | **SQL Databases** | [00-theory/database-concepts/](../../00-theory/database-concepts/) |
| | - ACID properties | |
| | - Normalization | |
| | - Indexing | |
| 1 hr | **NoSQL Databases** | |
| | - Document stores | |
| | - Key-value stores | |
| | - Wide-column stores | |
| | - Graph databases | |
| 30 min | **SQL vs NoSQL** | [CONCEPTS.md - Decision Trees](../../CONCEPTS.md#choosing-a-database) |

**Practice:**
- [ ] Design schema for a blog (SQL)
- [ ] Design schema for a product catalog (NoSQL)
- [ ] List 5 scenarios and choose SQL or NoSQL

---

### Day 4 (Thursday): Creational Patterns

| Time | Topic | Resources |
|------|-------|-----------|
| 45 min | **Singleton Pattern** | [01-design-patterns/creational/](../../01-design-patterns/creational/) |
| 45 min | **Factory Method Pattern** | |
| 45 min | **Abstract Factory Pattern** | |
| 45 min | **Builder Pattern** | |
| 30 min | **Prototype Pattern** | |

**For each pattern:**
- [ ] Understand the problem it solves
- [ ] Study the structure (UML)
- [ ] Implement in Java or Python
- [ ] Identify real-world use cases

---

### Day 5 (Friday): Structural Patterns

| Time | Topic | Resources |
|------|-------|-----------|
| 30 min | **Adapter Pattern** | [01-design-patterns/structural/adapter/](../../01-design-patterns/structural/adapter/) |
| 30 min | **Bridge Pattern** | [structural/bridge/](../../01-design-patterns/structural/bridge/) |
| 30 min | **Composite Pattern** | [structural/composite/](../../01-design-patterns/structural/composite/) |
| 30 min | **Decorator Pattern** | [structural/decorator/](../../01-design-patterns/structural/decorator/) |
| 30 min | **Facade Pattern** | [structural/facade/](../../01-design-patterns/structural/facade/) |
| 30 min | **Flyweight Pattern** | [structural/flyweight/](../../01-design-patterns/structural/flyweight/) |
| 30 min | **Proxy Pattern** | [structural/proxy/](../../01-design-patterns/structural/proxy/) |

**Practice:**
- [ ] Compare Adapter vs Bridge vs Decorator
- [ ] Implement Coffee shop with Decorator
- [ ] Implement File System with Composite

---

### Day 6 (Saturday): Behavioral Patterns (Part 1)

| Time | Topic | Resources |
|------|-------|-----------|
| 45 min | **Observer Pattern** | [01-design-patterns/behavioral/observer/](../../01-design-patterns/behavioral/observer/) |
| 45 min | **Strategy Pattern** | [behavioral/strategy/](../../01-design-patterns/behavioral/strategy/) |
| 45 min | **State Pattern** | [behavioral/state/](../../01-design-patterns/behavioral/state/) |
| 45 min | **Command Pattern** | [behavioral/command/](../../01-design-patterns/behavioral/command/) |
| 30 min | **Template Method** | [behavioral/template-method/](../../01-design-patterns/behavioral/template-method/) |

**Practice:**
- [ ] Implement notification system with Observer
- [ ] Implement payment processing with Strategy
- [ ] Compare Strategy vs State

---

### Day 7 (Sunday): Behavioral Patterns (Part 2) + Review

| Time | Topic | Resources |
|------|-------|-----------|
| 30 min | **Chain of Responsibility** | [01-design-patterns/behavioral/](../../01-design-patterns/behavioral/) |
| 30 min | **Iterator Pattern** | |
| 30 min | **Mediator Pattern** | |
| 30 min | **Memento Pattern** | |
| 30 min | **Visitor Pattern** | |
| 1 hr | **Week 1 Review** | |

**Review Activities:**
- [ ] Create pattern decision flowchart
- [ ] Quiz yourself on when to use each pattern
- [ ] Identify patterns in frameworks you use

---

### Week 1 Checkpoint ✅

Before moving to Week 2, ensure you can:
- [ ] Explain all 5 SOLID principles with examples
- [ ] Analyze time/space complexity of algorithms
- [ ] Decide between SQL and NoSQL for given scenarios
- [ ] Choose the right design pattern for a given problem
- [ ] Implement at least 10 patterns from scratch

---

## 📅 Week 2: LLD Projects

**Goal:** Apply design patterns and OOP principles to real-world LLD problems.

### Day 8 (Monday): LLD Framework + Parking Lot

| Time | Topic | Resources |
|------|-------|-----------|
| 1 hr | **LLD Approach Framework** | [02-lld-projects/HOW-TO-APPROACH.md](../../02-lld-projects/HOW-TO-APPROACH.md) |
| | - 7-step framework | [resources/templates/lld-template.md](../templates/lld-template.md) |
| | - Common interview tips | |
| 2.5 hrs | **Parking Lot System** | [02-lld-projects/parking-lot/](../../02-lld-projects/parking-lot/) |

**Practice:**
- [ ] Design Parking Lot from scratch (45 min timed)
- [ ] Compare with solution
- [ ] Note patterns used: Factory, Strategy, Singleton

---

### Day 9 (Tuesday): LRU Cache + Elevator System

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **LRU Cache** | [02-lld-projects/lru-cache/](../../02-lld-projects/lru-cache/) |
| 2 hrs | **Elevator System** | [02-lld-projects/elevator-system/](../../02-lld-projects/elevator-system/) |

**Focus Points:**
- LRU Cache: HashMap + Doubly Linked List, O(1) operations
- Elevator: State pattern for elevator states, Strategy for scheduling

---

### Day 10 (Wednesday): Library Management + Vending Machine

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Library Management** | [02-lld-projects/library-management/](../../02-lld-projects/library-management/) |
| 2 hrs | **Vending Machine** | [02-lld-projects/vending-machine/](../../02-lld-projects/vending-machine/) |

**Focus Points:**
- Library: User, Book, Loan, Reservation entities
- Vending Machine: State pattern for machine states

---

### Day 11 (Thursday): Hotel Reservation + Movie Ticket Booking

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Hotel Reservation** | [02-lld-projects/hotel-reservation/](../../02-lld-projects/hotel-reservation/) |
| 2 hrs | **Movie Ticket Booking** | [02-lld-projects/movie-ticket-booking/](../../02-lld-projects/movie-ticket-booking/) |

**Focus Points:**
- Both: Booking, Reservation, Payment handling
- Concurrency: Seat/Room locking during booking

---

### Day 12 (Friday): Car Rental + Ride Sharing

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Car Rental System** | [02-lld-projects/car-rental/](../../02-lld-projects/car-rental/) |
| 2 hrs | **Ride Sharing System** | [02-lld-projects/ride-sharing-system/](../../02-lld-projects/ride-sharing-system/) |

**Focus Points:**
- Car Rental: Vehicle hierarchy, Rental, Insurance
- Ride Sharing: Driver, Rider, Trip, matching strategy

---

### Day 13 (Saturday): Games (Chess, Tic-Tac-Toe, Snake & Ladder)

| Time | Topic | Resources |
|------|-------|-----------|
| 1.5 hrs | **Chess Game** | [02-lld-projects/chess-game/](../../02-lld-projects/chess-game/) |
| 1 hr | **Tic-Tac-Toe** | [02-lld-projects/tic-tac-toe/](../../02-lld-projects/tic-tac-toe/) |
| 1.5 hrs | **Snake and Ladder** | [02-lld-projects/snake-and-ladder/](../../02-lld-projects/snake-and-ladder/) |

**Focus Points:**
- Games: Board, Player, Move, GameState
- Chess: Piece hierarchy, Move validation

---

### Day 14 (Sunday): Week 2 Review + Practice

| Time | Topic | Resources |
|------|-------|-----------|
| 1.5 hrs | **Mock LLD #1** | Pick random problem |
| 1.5 hrs | **Mock LLD #2** | Pick random problem |
| 1 hr | **Week 2 Review** | |

**Review Activities:**
- [ ] Which patterns appear most frequently?
- [ ] Common entity relationships
- [ ] Edge cases to always consider

---

### Week 2 Checkpoint ✅

Before moving to Week 3, ensure you can:
- [ ] Apply the 7-step LLD framework consistently
- [ ] Design any of the 10 LLD projects in 45 minutes
- [ ] Identify which patterns to use for given requirements
- [ ] Handle concurrency and edge cases
- [ ] Explain trade-offs in your design choices

---

## 📅 Week 3: HLD Concepts + Systems

**Goal:** Master distributed systems concepts and design 4 systems.

### Day 15 (Monday): Load Balancing + Caching

| Time | Topic | Resources |
|------|-------|-----------|
| 1.5 hrs | **Load Balancing** | [CONCEPTS.md - Components](../../CONCEPTS.md#component-quick-reference) |
| | - Algorithms: Round Robin, Least Connections, IP Hash | |
| | - Layer 4 vs Layer 7 | |
| | - Health checks | |
| 2 hrs | **Caching** | [CONCEPTS.md - Caching](../../CONCEPTS.md#choosing-a-caching-strategy) |
| | - Cache strategies: Cache-aside, Write-through | |
| | - Eviction policies: LRU, LFU | |
| | - Redis vs Memcached | |
| | - CDN caching | |

---

### Day 16 (Tuesday): Database Scaling

| Time | Topic | Resources |
|------|-------|-----------|
| 1.5 hrs | **Sharding** | [03-hld-concepts/database-sharding/THEORY.md](../../03-hld-concepts/database-sharding/THEORY.md) |
| | - Horizontal vs Vertical partitioning | |
| | - Sharding strategies | |
| | - Consistent hashing | [03-hld-concepts/consistent-hashing/THEORY.md](../../03-hld-concepts/consistent-hashing/THEORY.md) |
| 1 hr | **Replication** | [03-hld-concepts/database-replication/](../../03-hld-concepts/database-replication/) |
| | - Master-Slave, Master-Master | |
| | - Sync vs Async replication | |
| 1 hr | **CAP Theorem** | [03-hld-concepts/cap-theorem/THEORY.md](../../03-hld-concepts/cap-theorem/THEORY.md) |
| | - Endpoint-level policy choices | |
| | - Degraded mode + reconciliation | |

---

### Day 17 (Wednesday): Async Processing + API Design

| Time | Topic | Resources |
|------|-------|-----------|
| 1.5 hrs | **Message Queues** | [CONCEPTS.md - Communication](../../CONCEPTS.md#choosing-communication-pattern) |
| | - Kafka, RabbitMQ, SQS | |
| | - Message ordering | |
| | - Consumer groups | |
| 1 hr | **API Design** | |
| | - REST principles | |
| | - Versioning | |
| | - Pagination | |
| 1 hr | **Rate Limiting** | |
| | - Token bucket, Sliding window | |
| | - Distributed rate limiting | |

---

### Day 18 (Thursday): HLD Template + URL Shortener

| Time | Topic | Resources |
|------|-------|-----------|
| 30 min | **HLD Template Review** | [04-hld-projects/DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md) |
| | | [resources/templates/hld-template.md](../templates/hld-template.md) |
| 3 hrs | **Design: URL Shortener** | [04-hld-projects/](../../04-hld-projects/) |
| | - Requirements & Estimations | |
| | - API & Data Model | |
| | - Architecture & Deep Dives | |

**Key Points:**
- Hash function (Base62), Read-heavy (cache), Analytics

---

### Day 19 (Friday): Twitter Feed / Timeline

| Time | Topic | Resources |
|------|-------|-----------|
| 3.5 hrs | **Design: Twitter/Feed System** | [04-hld-projects/](../../04-hld-projects/) |
| | - Fan-out on Write vs Read | |
| | - Celebrity problem | |
| | - Timeline caching | |

**Key Points:**
- Hybrid approach, Timeline service, Follow graph

---

### Day 20 (Saturday): Chat Application

| Time | Topic | Resources |
|------|-------|-----------|
| 3.5 hrs | **Design: Chat Application** | [04-hld-projects/](../../04-hld-projects/) |
| | - WebSockets | |
| | - Message delivery guarantees | |
| | - Presence service | |

**Key Points:**
- Real-time communication, Message ordering, Multi-device

---

### Day 21 (Sunday): Video Streaming + Week 3 Review

| Time | Topic | Resources |
|------|-------|-----------|
| 2.5 hrs | **Design: Video Streaming** | [04-hld-projects/](../../04-hld-projects/) |
| | - Video upload & transcoding | |
| | - CDN & Adaptive streaming | |
| 1 hr | **Week 3 Review** | |

---

### Week 3 Checkpoint ✅

Before moving to Week 4, ensure you can:
- [ ] Explain load balancing, caching, sharding in depth
- [ ] Choose between CP and AP for given requirements
- [ ] Explain consistent-hash remap benefits vs hotspot limitations
- [ ] Design URL Shortener in 45 minutes
- [ ] Explain fan-out strategies for social feeds
- [ ] Design a real-time chat system
- [ ] Explain video streaming architecture
- [ ] Score 23+/30 in [hld-concepts-quiz.md](../../quizzes/hld-concepts-quiz.md) or complete one run of [practice-hld-core-concepts.md](../templates/practice-hld-core-concepts.md)

---

## 📅 Week 4: Advanced Systems + Mock Practice

**Goal:** Master 4 more systems, practice mocks, and prepare for interview.

### Day 22 (Monday): Uber / Ride Sharing System

| Time | Topic | Resources |
|------|-------|-----------|
| 3.5 hrs | **Design: Uber** | [04-hld-projects/](../../04-hld-projects/) |
| | - Location tracking | |
| | - Driver-rider matching | |
| | - Surge pricing | |

**Key Points:**
- Geospatial indexing (QuadTree, Geohash), ETA calculation

---

### Day 23 (Tuesday): E-commerce / Amazon

| Time | Topic | Resources |
|------|-------|-----------|
| 3.5 hrs | **Design: E-commerce** | [04-hld-projects/](../../04-hld-projects/) |
| | - Product catalog | |
| | - Cart & Checkout | |
| | - Inventory management | |

**Key Points:**
- Inventory consistency, Payment processing, Order management

---

### Day 24 (Wednesday): Notification System + Rate Limiter

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Design: Notification System** | [04-hld-projects/](../../04-hld-projects/) |
| | - Push, SMS, Email channels | |
| | - Priority & batching | |
| 2 hrs | **Design: Rate Limiter** | [02-lld-projects/rate-limiter/](../../02-lld-projects/rate-limiter/) |
| | - Token bucket, Sliding window | |
| | - Distributed implementation | |

---

### Day 25 (Thursday): Mock Interview Day #1

| Time | Activity |
|------|----------|
| 1 hr | **LLD Mock #1** - Random problem (45 min timed + review) |
| 1 hr | **LLD Mock #2** - Random problem (45 min timed + review) |
| 1 hr | **HLD Mock #1** - Random system (45 min timed + review) |
| 30 min | **Self-assessment** - Note strengths and weaknesses |

---

### Day 26 (Friday): Mock Interview Day #2

| Time | Activity |
|------|----------|
| 1 hr | **HLD Mock #2** - Random system (45 min timed + review) |
| 1 hr | **HLD Mock #3** - Weak area system (45 min timed + review) |
| 1 hr | **Mixed Mock** - Interview asks LLD or HLD |
| 30 min | **Self-assessment** - Compare with Day 25 |

---

### Day 27 (Saturday): Deep Review Day

| Time | Activity | Resources |
|------|----------|-----------|
| 1 hr | **Cheatsheets Review** | [resources/cheatsheets/](../cheatsheets/) |
| 1 hr | **Interview Tips** | [resources/interview-tips/](../interview-tips/) + [interview-framework.md](../interview-tips/interview-framework.md) |
| 1 hr | **Weak Areas** | Focus on identified gaps |
| 1 hr | **Trade-offs Practice** | Review all trade-off decisions |

---

### Day 28 (Sunday): Final Preparation

| Time | Activity |
|------|----------|
| 1 hr | **Quick Pattern Drill** - 2 min per pattern |
| 1 hr | **Quick System Drill** - 5 min per system |
| 1 hr | **Estimation Practice** - QPS, storage calculations ([guide](../../00-theory/system-design-fundamentals/back-of-envelope.md)) |
| 30 min | **Final Checklist** - Everything ready for interview |

---

### Week 4 Checkpoint ✅

Before the interview, ensure you can:
- [ ] Design any of the 8 HLD systems in 45 minutes
- [ ] Handle curve-ball questions gracefully
- [ ] Explain trade-offs clearly
- [ ] Manage time effectively
- [ ] Communicate design decisions confidently

---

## 📈 Full Month Progress Tracker

```markdown
## My 1-Month Progress

### Week 1: Foundations + Patterns
- [ ] Day 1: OOP + SOLID
- [ ] Day 2: Complexity Analysis
- [ ] Day 3: Database Fundamentals
- [ ] Day 4: Creational Patterns (5)
- [ ] Day 5: Structural Patterns (7)
- [ ] Day 6: Behavioral Patterns Part 1 (5)
- [ ] Day 7: Behavioral Patterns Part 2 + Review

### Week 2: LLD Projects
- [ ] Day 8: LLD Framework + Parking Lot
- [ ] Day 9: LRU Cache + Elevator
- [ ] Day 10: Library + Vending Machine
- [ ] Day 11: Hotel + Movie Ticket
- [ ] Day 12: Car Rental + Ride Sharing
- [ ] Day 13: Chess + Tic-Tac-Toe + Snake & Ladder
- [ ] Day 14: Week 2 Review + Mocks

### Week 3: HLD Concepts + Systems
- [ ] Day 15: Load Balancing + Caching
- [ ] Day 16: Sharding + Replication + CAP + Consistent Hashing
- [ ] Day 17: Message Queues + API + Rate Limiting
- [ ] Day 18: HLD Template + URL Shortener
- [ ] Day 19: Twitter Feed
- [ ] Day 20: Chat Application
- [ ] Day 21: Video Streaming + Review

### Week 4: Advanced + Practice
- [ ] Day 22: Uber Design
- [ ] Day 23: E-commerce Design
- [ ] Day 24: Notification + Rate Limiter
- [ ] Day 25: Mock Day #1
- [ ] Day 26: Mock Day #2
- [ ] Day 27: Deep Review
- [ ] Day 28: Final Preparation
```

---

## 🎯 Accelerated Plans

### 2-Week Plan (Skip Week 1)
If you already have strong fundamentals:
- **Week 1** → Week 2 content (LLD)
- **Week 2** → Weeks 3-4 content (HLD + Practice)

### 3-Week Plan (Condensed)
- **Week 1** → Patterns (Days 4-7 only) + 4 LLD projects
- **Week 2** → HLD concepts + 4 systems
- **Week 3** → 4 more systems + Mock practice

---

## 📌 Key Success Factors

1. **Consistency** - Study every day, even if just 1-2 hours
2. **Active practice** - Don't just read, implement and design
3. **Timed practice** - Use 45-minute sessions like real interviews
4. **Self-assessment** - Honestly evaluate your progress
5. **Rest** - Don't burn out, take breaks

---

*You've got this! 4 weeks of focused effort will prepare you well. 🚀*

---

## March 2026 Extended Tracks

- Include `social-post-search` and `price-tracking-service` as advanced classic HLD drills.
- Add source 24-28 progression:
  - `metrics-monitoring` → `realtime-metrics-platform`
  - `job-scheduler`, `web-crawler`, `ad-click-aggregator`, `payment-system`
