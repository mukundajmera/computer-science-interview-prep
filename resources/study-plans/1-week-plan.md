# 🚨 1-Week Crash Course

A focused 7-day plan to prepare for system design interviews when time is limited.

---

## 📋 Overview

| Day | Focus Area | Time | Topics |
|-----|------------|------|--------|
| 1 | Core Design Patterns | 5-6 hrs | Singleton, Factory, Strategy, Observer, Builder, Decorator |
| 2 | LLD Projects (Part 1) | 5-6 hrs | Parking Lot, LRU Cache, Elevator System |
| 3 | HLD Concepts | 5-6 hrs | Caching, Load Balancing, Sharding, Message Queues |
| 4 | HLD Systems (Part 1) | 5-6 hrs | URL Shortener, Twitter Feed |
| 5 | HLD Systems (Part 2) | 5-6 hrs | Chat Application, Video Streaming |
| 6 | Mock Practice | 4-5 hrs | Self-practice mock interviews |
| 7 | Review & Polish | 3-4 hrs | Cheatsheets, weak areas, rest |

**Total Time:** ~35-40 hours

---

## 📅 Day 1: Core Design Patterns

**Goal:** Master the 6 most commonly asked design patterns.

### Morning Session (2-3 hrs)

#### 🎯 Creational Patterns
- [ ] **Singleton Pattern** (45 min)
  - 📁 Study: [01-design-patterns/creational/](../../01-design-patterns/)
  - 📖 Reference: [CONCEPTS.md - Creational Patterns](../../CONCEPTS.md#creational-patterns)
  - ✍️ Practice: Implement thread-safe Singleton in Java/Python
  - 💡 Key point: Lazy initialization, double-checked locking

- [ ] **Factory Method Pattern** (45 min)
  - 📁 Study: [01-design-patterns/creational/](../../01-design-patterns/)
  - ✍️ Practice: Create a VehicleFactory that creates Car, Bike, Truck
  - 💡 Key point: Decouple object creation from usage

- [ ] **Builder Pattern** (30 min)
  - 📁 Study: [01-design-patterns/creational/](../../01-design-patterns/)
  - ✍️ Practice: Build a Pizza or User object with multiple optional fields
  - 💡 Key point: Use when constructor has 4+ parameters

### Afternoon Session (2-3 hrs)

#### 🎯 Behavioral Patterns
- [ ] **Strategy Pattern** (45 min)
  - 📁 Study: [01-design-patterns/behavioral/strategy/](../../01-design-patterns/behavioral/strategy/)
  - ✍️ Practice: Implement PaymentProcessor with CreditCard, PayPal, UPI strategies
  - 💡 Key point: Encapsulate algorithms, swap at runtime

- [ ] **Observer Pattern** (45 min)
  - 📁 Study: [01-design-patterns/behavioral/observer/](../../01-design-patterns/behavioral/observer/)
  - ✍️ Practice: Create a NewsPublisher with multiple Subscriber types
  - 💡 Key point: One-to-many dependency, push vs pull

#### 🎯 Structural Patterns
- [ ] **Decorator Pattern** (45 min)
  - 📁 Study: [01-design-patterns/structural/decorator/](../../01-design-patterns/structural/decorator/)
  - ✍️ Practice: Coffee shop with toppings (Milk, Sugar, Whip)
  - 💡 Key point: Add behavior without inheritance

### Evening Review (1 hr)

- [ ] **Pattern Decision Practice** (30 min)
  - Given scenarios, identify which pattern to use:
    - "Need only one database connection" → Singleton
    - "Different notification types (Email, SMS, Push)" → Factory
    - "Multiple payment methods at checkout" → Strategy
    - "Real-time stock price updates to clients" → Observer

- [ ] **Quick Notes** (30 min)
  - Create your own pattern summary card
  - Note common interview questions for each pattern

---

## 📅 Day 2: LLD Projects (Part 1)

**Goal:** Practice 3 foundational LLD problems end-to-end.

### Morning Session (2.5 hrs)

- [ ] **Review LLD Approach** (30 min)
  - 📁 Study: [02-lld-projects/HOW-TO-APPROACH.md](../../02-lld-projects/HOW-TO-APPROACH.md)
  - 📁 Template: [resources/templates/lld-template.md](../templates/lld-template.md)
  - Key framework: Clarify → Entities → Relationships → Patterns → Classes → Edge Cases

- [ ] **Parking Lot System** (2 hrs)
  - 📁 Study: [02-lld-projects/parking-lot/](../../02-lld-projects/parking-lot/)
  - ✍️ Practice:
    1. Identify entities: ParkingLot, Floor, ParkingSpot, Vehicle, Ticket
    2. Define relationships (composition vs aggregation)
    3. Apply patterns: Factory (vehicles), Strategy (pricing)
    4. Design core classes with attributes and methods
    5. Handle edge cases: lot full, invalid ticket, concurrent parking

### Afternoon Session (2.5 hrs)

- [ ] **LRU Cache** (1.5 hrs)
  - 📁 Study: [02-lld-projects/lru-cache/](../../02-lld-projects/lru-cache/)
  - ✍️ Practice:
    1. Understand data structure: HashMap + Doubly Linked List
    2. Implement `get()` and `put()` operations
    3. Handle cache eviction
    4. Analyze: O(1) for both operations
  - 💡 Key point: Very common in both LLD and coding interviews

- [ ] **Elevator System** (1 hr)
  - 📁 Study: [02-lld-projects/elevator-system/](../../02-lld-projects/elevator-system/)
  - ✍️ Practice:
    1. Entities: Elevator, ElevatorController, Floor, Request
    2. States: Moving, Idle, Stopped
    3. Apply patterns: State pattern for elevator states, Strategy for scheduling
    4. Handle multiple elevators

### Evening Review (1 hr)

- [ ] **Compare Solutions** (30 min)
  - Compare your design with repo solutions
  - Note differences and improvements

- [ ] **Complexity Analysis** (30 min)
  - For each project, document:
    - Time complexity of main operations
    - Space complexity
    - Data structure choices and why

---

## 📅 Day 3: HLD Concepts

**Goal:** Master the building blocks of distributed systems.

### Morning Session (2.5 hrs)

- [ ] **Load Balancing** (45 min)
  - 📁 Reference: [CONCEPTS.md - Components](../../CONCEPTS.md#component-quick-reference)
  - Topics to cover:
    - Round robin, Weighted, Least connections, IP hash
    - Layer 4 vs Layer 7 load balancing
    - Health checks
    - When to use: High traffic, redundancy, horizontal scaling

- [ ] **Caching** (60 min)
  - Topics to cover:
    - Cache-aside, Write-through, Write-behind, Write-around
    - Cache invalidation strategies (TTL, event-based)
    - Cache eviction policies (LRU, LFU, FIFO)
    - Redis vs Memcached
    - CDN caching
  - 💡 Key point: "Cache invalidation is one of the two hard things in CS"

- [ ] **CAP Theorem** (45 min)
  - 📁 Reference: [CONCEPTS.md - CAP Theorem](../../CONCEPTS.md#cap-theorem)
  - 📁 Deep dive: [03-hld-concepts/cap-theorem/THEORY.md](../../03-hld-concepts/cap-theorem/THEORY.md)
  - Topics to cover:
    - Operation-level consistency vs availability decisions
    - Critical-write vs browse-read policies
    - Degraded-mode behavior under partition
    - Reconciliation expectations after recovery

### Afternoon Session (2.5 hrs)

- [ ] **Database Sharding** (60 min)
  - 📁 Deep dive: [03-hld-concepts/database-sharding/THEORY.md](../../03-hld-concepts/database-sharding/THEORY.md)
  - Topics to cover:
    - Horizontal vs Vertical partitioning
    - Sharding strategies: Range, Hash, Directory-based
    - Consistent hashing
    - Challenges: Cross-shard queries, Rebalancing
    - When to shard vs not shard

- [ ] **Database Replication** (45 min)
  - Topics to cover:
    - Master-Slave (Primary-Replica)
    - Master-Master
    - Synchronous vs Asynchronous replication
    - Replication lag
    - Read replicas for read scaling

- [ ] **Message Queues** (45 min)
  - Topics to cover:
    - Why async processing (decouple, buffer, scale)
    - Kafka vs RabbitMQ vs SQS
    - Message ordering and delivery guarantees
    - Consumer groups
    - When to use: Email, notifications, heavy processing

### Evening Review (1 hr)

- [ ] **System Design Component Map** (30 min)
  - 📁 Review: [CONCEPTS.md - Components Map](../../CONCEPTS.md#system-design-components-map)
  - Practice: "Which components for a social media feed?"
  - Practice: "Which components for a ride-sharing app?"

- [ ] **Trade-offs Summary** (30 min)
  - SQL vs NoSQL
  - Consistency vs Availability
  - Sync vs Async
  - Push vs Pull

- [ ] **Core Concepts Drill** (optional 20 min)
  - 📁 Template: [resources/templates/practice-hld-core-concepts.md](../templates/practice-hld-core-concepts.md)
  - 📁 Quiz: [quizzes/hld-concepts-quiz.md](../../quizzes/hld-concepts-quiz.md)
  - 📁 Flashcards: [flashcards/hld-concepts.md](../../flashcards/hld-concepts.md)

---

## 📅 Day 4: HLD Systems (Part 1)

**Goal:** Deep dive into 2 classic system design problems.

### Morning Session (2.5 hrs)

- [ ] **URL Shortener (like bit.ly)** (2.5 hrs)
  - 📁 Study: [04-hld-projects/](../../04-hld-projects/)
  - 📁 Template: [resources/templates/hld-template.md](../templates/hld-template.md)
  - 📁 Approach: [04-hld-projects/DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md)
  
  #### Requirements
  - Shorten long URL → short URL
  - Redirect short URL → original URL
  - Custom aliases (optional)
  - Analytics (optional)
  - 100M URLs created/month
  
  #### Key Design Points
  - Hash function: MD5/SHA256 truncated, or counter + Base62
  - Database: NoSQL (DynamoDB/Cassandra) for simple key-value
  - Read-heavy: 100:1 read to write ratio → Cache heavily
  - Short URL format: 6-7 characters = 3.5B unique URLs
  
  #### Estimations Practice
  - 100M writes/month = ~40 writes/second
  - 10B reads/month = ~4000 reads/second
  - Storage: 500 bytes/URL × 100M × 12 months × 5 years = 3TB

### Afternoon Session (2.5 hrs)

- [ ] **Twitter Feed / Timeline** (2.5 hrs)
  - 📁 Study: [04-hld-projects/](../../04-hld-projects/)
  
  #### Requirements
  - Post tweets
  - Follow users
  - View home timeline (tweets from followed users)
  - 500M users, 200M DAU
  
  #### Key Design Points
  - Fan-out on write vs Fan-out on read
    - Write: Pre-compute feeds (good for most users)
    - Read: Compute on demand (good for celebrities)
    - Hybrid: Both approaches based on follower count
  - Timeline service, Tweet service, User service
  - Cache: Redis for hot timelines
  - Database: Sharded by user_id
  
  #### Trade-offs to Discuss
  - Fan-out trade-offs
  - Push vs Pull model
  - Consistency of timeline

### Evening Review (1 hr)

- [ ] **Practice Explaining** (30 min)
  - Set a timer for 5 minutes
  - Explain URL Shortener design out loud
  - Repeat for Twitter Feed

- [ ] **Note Common Questions** (30 min)
  - "What if short URL collides?"
  - "How to handle celebrity users?"
  - "How to scale to 10x traffic?"

---

## 📅 Day 5: HLD Systems (Part 2)

**Goal:** Deep dive into 2 more system design problems.

### Morning Session (2.5 hrs)

- [ ] **Chat Application (like WhatsApp/Slack)** (2.5 hrs)
  - 📁 Study: [04-hld-projects/](../../04-hld-projects/)
  
  #### Requirements
  - 1:1 messaging
  - Group messaging
  - Online/offline status
  - Message delivery status (sent, delivered, read)
  - 50M DAU
  
  #### Key Design Points
  - WebSockets for real-time bidirectional communication
  - Connection manager: Which server holds which user's connection
  - Message queue: Kafka/RabbitMQ for async delivery
  - Presence service: Redis for online status with TTL
  - Database: Cassandra/HBase for messages (write-heavy, time-series)
  
  #### Deep Dive Topics
  - How to handle user on multiple devices
  - Message ordering (timestamps, vector clocks)
  - Group message fan-out
  - End-to-end encryption

### Afternoon Session (2.5 hrs)

- [ ] **Video Streaming (like YouTube/Netflix)** (2.5 hrs)
  - 📁 Study: [04-hld-projects/](../../04-hld-projects/)
  
  #### Requirements
  - Upload videos
  - Stream videos
  - Search videos
  - Recommendations (optional)
  - 1B daily video views
  
  #### Key Design Points
  - CDN: Edge servers for global content delivery
  - Blob storage: S3/GCS for video files
  - Transcoding: Convert to multiple formats/resolutions
  - Adaptive bitrate streaming (HLS/DASH)
  - Video processing pipeline: Upload → Transcode → Store → CDN
  
  #### Deep Dive Topics
  - How CDN works
  - Video encoding and formats
  - Chunked upload for large files
  - Recommendation system overview

### Evening Review (1 hr)

- [ ] **Compare All 4 Systems** (30 min)
  - Which components appear in multiple systems?
  - Common patterns across systems
  
- [ ] **Weakness Identification** (30 min)
  - Which system do you understand least?
  - Which concepts are still unclear?
  - Note for Day 7 review

---

## 📅 Day 6: Mock Practice

**Goal:** Practice under interview conditions.

### Morning Session (2 hrs)

- [ ] **LLD Mock Interview #1** (1 hr)
  - Pick a random problem: Vending Machine, Library Management, or Hotel Booking
  - 📁 Problems: [02-lld-projects/](../../02-lld-projects/)
  - Set a 45-minute timer
  - Practice:
    1. Clarify requirements (5 min)
    2. Identify entities (5 min)
    3. Design classes (20 min)
    4. Apply patterns (10 min)
    5. Handle edge cases (5 min)

- [ ] **LLD Mock Interview #2** (1 hr)
  - Pick another problem: Tic-Tac-Toe, ATM System, or Snake and Ladder
  - Follow the same process
  - Record yourself or practice with a friend

### Afternoon Session (2 hrs)

- [ ] **HLD Mock Interview #1** (1 hr)
  - Pick: Design a Rate Limiter or Design Uber
  - Set a 45-minute timer
  - Practice:
    1. Requirements clarification (5 min)
    2. Estimations (5 min)
    3. API design (5 min)
    4. High-level architecture (15 min)
    5. Deep dives (10 min)
    6. Trade-offs (5 min)

- [ ] **HLD Mock Interview #2** (1 hr)
  - Pick: Design Instagram or Design Notification System
  - Follow the same process
  - Focus on areas you struggled with earlier

### Evening Review (1 hr)

- [ ] **Self-Assessment** (30 min)
  - What went well in each mock?
  - Where did you struggle?
  - Did you manage time well?
  - Did you think out loud?

- [ ] **Improvement Plan** (30 min)
  - List 3 things to improve
  - Plan specific practice for Day 7

---

## 📅 Day 7: Review & Polish

**Goal:** Consolidate knowledge, rest before interview.

### Morning Session (1.5 hrs)

- [ ] **Cheatsheet Review** (1 hr)
  - 📁 Review: [resources/cheatsheets/](../cheatsheets/)
  - 📁 Review: [CONCEPTS.md](../../CONCEPTS.md)
  - Focus on:
    - Pattern decision tree
    - Component selection guide
    - Trade-offs matrix
    - Back-of-envelope numbers ([guide](../../00-theory/system-design-fundamentals/back-of-envelope.md))

- [ ] **Weak Areas** (30 min)
  - Review topics identified on Day 5 & 6
  - Quick practice on weakest system

### Afternoon Session (1.5 hrs)

- [ ] **Interview Tips Review** (30 min)
  - 📁 Review: [resources/interview-tips/](../interview-tips/)
  - 📁 Framework: [interview-framework.md](../interview-tips/interview-framework.md)
  - Focus on:
    - Communication guide
    - Common pitfalls to avoid
    - Time management

- [ ] **Quick Pattern Drill** (30 min)
  - For each pattern, state:
    - When to use (one sentence)
    - Real example
    - Key classes/interfaces

- [ ] **Quick System Drill** (30 min)
  - For each system, state:
    - 3 key components
    - Main trade-off
    - Most common follow-up question

### Evening (1 hr)

- [ ] **Rest and Prepare** (1 hr)
  - Light review only
  - Prepare logistics (water, paper, pen)
  - Test your internet/video if remote
  - Get good sleep!

---

## 📌 Daily Checklist Summary

### Each Day Should Include:
- [ ] Morning study session (2-3 hrs)
- [ ] Afternoon practice session (2-3 hrs)
- [ ] Evening review (1 hr)
- [ ] Note at least 3 key learnings
- [ ] Identify 1 weak area to revisit

### What to Have Ready:
- [ ] Notebook for diagrams
- [ ] IDE for code practice
- [ ] Timer for mock interviews
- [ ] This checklist printed or open

---

## 🎯 Priority Focus (If Short on Time)

**Must Master (Essential):**
- Patterns: Singleton, Factory, Strategy, Observer
- LLD: Parking Lot, LRU Cache
- HLD: URL Shortener, Twitter Feed
- Concepts: Caching, Load Balancing, CAP

**Should Know (Important):**
- Patterns: Builder, Decorator, State
- LLD: Elevator System
- HLD: Chat App, Video Streaming
- Concepts: Sharding, Message Queues

**Good to Know (Bonus):**
- Other patterns: Adapter, Facade, Command
- Other LLD: Vending Machine, Library
- Other HLD: Uber, Rate Limiter
- Concepts: Consistent Hashing, Replication

---

## 📈 Progress Tracker

Copy this checklist to track your progress:

```markdown
## My 1-Week Progress

### Day 1: Design Patterns
- [ ] Singleton
- [ ] Factory
- [ ] Builder
- [ ] Strategy
- [ ] Observer
- [ ] Decorator

### Day 2: LLD Projects
- [ ] HOW-TO-APPROACH review
- [ ] Parking Lot
- [ ] LRU Cache
- [ ] Elevator System

### Day 3: HLD Concepts
- [ ] Load Balancing
- [ ] Caching
- [ ] CAP Theorem
- [ ] Sharding
- [ ] Replication
- [ ] Message Queues
- [ ] Core concepts drill (template + quiz + flashcards)

### Day 4: HLD Systems Part 1
- [ ] URL Shortener
- [ ] Twitter Feed

### Day 5: HLD Systems Part 2
- [ ] Chat Application
- [ ] Video Streaming

### Day 6: Mock Practice
- [ ] LLD Mock #1
- [ ] LLD Mock #2
- [ ] HLD Mock #1
- [ ] HLD Mock #2

### Day 7: Review
- [ ] Cheatsheet review
- [ ] Weak areas review
- [ ] Final preparation
```

---

*Good luck with your interview! 🍀*

---

## March 2026 Optional Add-on Pack

- Add one new problem from source-set tracks: `online-auction` or `live-comments`.
- Add one LLD from source 24-28: `job-scheduler` or `payment-system`.
- Add one HLD from source 24-28: `metrics-monitoring` or `web-crawler`.
