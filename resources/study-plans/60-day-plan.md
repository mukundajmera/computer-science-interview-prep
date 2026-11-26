# 📚 60-Day Study Plan (SDE II to Senior)

A comprehensive 8-9 week plan (~15 hrs/week) tailored for SDE II through Senior SDE candidates. This plan covers fundamental principles, design patterns, high-frequency LLD and HLD problems, GenAI systems, and mock interviews to calibrate your system design and behavioral interview skills.


---

## 📋 Overview

| Phase | Weeks | Focus Area | Expected Hours |
|-------|-------|------------|----------------|
| **Phase 1** | Weeks 1-2 | CS Fundamentals & Patterns | ~15 hrs/week |
| **Phase 2** | Weeks 3-5 | High-Frequency LLD | ~15 hrs/week |
| **Phase 3** | Weeks 6-7 | Distributed Systems & HLD | ~15 hrs/week |
| **Phase 4** | Week 8 | GenAI Systems | ~15 hrs/week |
| **Phase 5** | Week 9 | Mock Interviews & Calibration | ~15 hrs total |



**Total Time:** ~135 hours over 9 weeks

---

## 📅 Phase 1: Weeks 1-2 - CS Fundamentals & Patterns

**Goal:** Establish a strong foundation in Object-Oriented Programming (OOP), SOLID principles, and essential Design Patterns.

### Week 1: Core Principles & Creational/Structural Patterns

**Day 1: OOP Principles & SOLID**
- **Reading List:**
  - `00-theory/oop-principles/encapsulation-abstraction.md`
  - `00-theory/oop-principles/solid-principles.md`
- **Coding Drills:**
  - Implement a basic parking lot skeleton focusing purely on Single Responsibility and Open/Closed principles.
- **Quiz Checkpoint:** Identify SOLID violations in a provided 100-line monolithic script.

**Day 2: Creational Patterns (Singleton, Factory, Builder)**
- **Reading List:**
  - `01-design-patterns/creational/singleton/THEORY.md`
  - `01-design-patterns/creational/factory-method/THEORY.md`
  - `01-design-patterns/creational/builder/THEORY.md`
- **Coding Drills:**
  - Build a thread-safe Singleton configuration manager.
  - Create a Document Builder that can export to PDF or HTML.

**Day 3: Creational Patterns (Abstract Factory, Prototype) & Review**
- **Reading List:**
  - `01-design-patterns/creational/abstract-factory/THEORY.md`
  - `01-design-patterns/creational/prototype/THEORY.md`
- **Coding Drills:**
  - Implement a UI toolkit using Abstract Factory (Windows vs. Mac).
- **Quiz Checkpoint:** Creational Patterns matching quiz.

**Day 4: Structural Patterns (Adapter, Bridge, Composite)**
- **Reading List:**
  - `01-design-patterns/structural/adapter/THEORY.md`
  - `01-design-patterns/structural/bridge/THEORY.md`
  - `01-design-patterns/structural/composite/THEORY.md`
- **Coding Drills:**
  - Adapter for a legacy payment gateway (Stripe vs Legacy API).
  - Composite pattern for a File System directory structure.

**Day 5: Structural Patterns (Decorator, Facade, Proxy)**
- **Reading List:**
  - `01-design-patterns/structural/decorator/THEORY.md`
  - `01-design-patterns/structural/facade/THEORY.md`
  - `01-design-patterns/structural/proxy/THEORY.md`
- **Coding Drills:**
  - Decorator for a coffee shop (Base coffee + Milk, Mocha, etc.).
  - Proxy for a database connection with lazy initialization and access control.

**Day 6-7: Weekend Review & Catch-up**
- Complete pending readings.
- **Scorecard Rubric (Week 1):** Can you implement all 3 creational patterns from memory? (Yes: 5 pts, No: 0 pts).

### Week 2: Behavioral Patterns & Concurrency

**Day 8: Behavioral Patterns (Strategy, Observer, Command)**
- **Reading List:**
  - `01-design-patterns/behavioral/strategy/THEORY.md`
  - `01-design-patterns/behavioral/observer/THEORY.md`
  - `01-design-patterns/behavioral/command/THEORY.md`
- **Coding Drills:**
  - Implement a sorting strategy selector.
  - Create a publisher/subscriber event bus using Observer.

**Day 9: Behavioral Patterns (State, Chain of Responsibility, Iterator)**
- **Reading List:**
  - `01-design-patterns/behavioral/state/THEORY.md`
  - `01-design-patterns/behavioral/chain-of-responsibility/THEORY.md`
  - `01-design-patterns/behavioral/iterator/THEORY.md`
- **Coding Drills:**
  - Vending Machine using State pattern.
  - Logging framework using Chain of Responsibility.

**Day 10: Behavioral Patterns (Mediator, Memento, Visitor)**
- **Reading List:**
  - `01-design-patterns/behavioral/mediator/THEORY.md`
  - `01-design-patterns/behavioral/memento/THEORY.md`
- **Coding Drills:**
  - Chat room using Mediator.
  - Undo/Redo functionality using Memento.

**Day 11: Concurrency Basics (Threads, Locks, Semaphores)**
- **Reading List:**
  - `00-theory/concurrency/synchronization-primitives-and-barriers.md`
- **Coding Drills:**
  - Thread-safe bounded blocking queue.

**Day 12: Advanced Concurrency & Deadlock Prevention**
- **Reading List:**
  - `00-theory/concurrency/deadlock-theory-and-coffman-conditions.md`
- **Coding Drills:**
  - Simulate a bank transfer between accounts highlighting deadlock and then fixing it via lock ordering.

**Day 13-14: Weekend Review & Phase 1 Assessment**
- **Quiz Checkpoint:** Comprehensive 20-question quiz on Design Patterns.
- **Scorecard Rubric (Week 2):** Evaluate ability to recognize patterns in real-world scenarios.

---

## 📅 Phase 2: Weeks 3-5 - High-Frequency LLD

**Goal:** Master Low-Level Design (LLD) by practicing the most commonly asked interview questions. Focus on class diagrams, API design, and core algorithms.

### Week 3: Essential Real-world LLD

**Day 15-16: Parking Lot System**
- **Reading List:** `02-lld-projects/parking-lot/PROBLEM.md`
- **Coding Drills:**
  - Class structure and Enum definitions.
  - Logic for finding an empty spot (nearest to entrance).
- **Scorecard Rubric:** Is the code extensible to add new vehicle types?

**Day 17-18: Vending Machine**
- **Reading List:** `02-lld-projects/vending-machine/PROBLEM.md`
- **Coding Drills:**
  - State pattern implementation for machine states (Idle, HasMoney, Dispensing).
- **Quiz Checkpoint:** Handling edge cases (insufficient funds, out of stock).

**Day 19-20: Elevator System**
- **Reading List:** `02-lld-projects/elevator-system/PROBLEM.md`
- **Coding Drills:**
  - Dispatch algorithm (SCAN / LOOK).
  - Thread-safe request queuing.

**Day 21: Review & Buffer**

### Week 4: Concurrency & Booking Systems

**Day 22-23: Movie Ticket Booking System (BookMyShow)**
- **Reading List:** `02-lld-projects/movie-ticket-booking/PROBLEM.md`
- **Coding Drills:**
  - Handling concurrency during seat selection (optimistic vs pessimistic locking).
  - Database schema for theaters, screens, shows, seats.

**Day 24-25: Ride Sharing Service (Uber)**
- **Reading List:** `02-lld-projects/ride-sharing-system/PROBLEM.md`
- **Coding Drills:**
  - Strategy pattern for pricing (Surge vs Normal).
  - Matching algorithm skeleton.

**Day 26-27: Restaurant Management System**
- **Reading List:** `02-lld-projects/restaurant-management/PROBLEM.md`
- **Coding Drills:**
  - Order fulfillment workflow (Observer pattern).
  - Table reservation logic.

**Day 28: Review & Buffer**
- **Quiz Checkpoint:** Concurrency handling in transactional systems.

### Week 5: Complex Workflows & Games

**Day 29-30: Task Scheduler / Job Queue**
- **Reading List:** `02-lld-projects/job-scheduler/PROBLEM.md`
- **Coding Drills:**
  - Delayed execution logic (Cron expressions).
  - Handling worker failures and retries.

**Day 31-32: Chess Game**
- **Reading List:** `02-lld-projects/chess-game/PROBLEM.md`
- **Coding Drills:**
  - Class hierarchy for Pieces.
  - Validation logic for moves and checkmate detection.

**Day 33-34: Snake and Ladders / Tic Tac Toe**
- **Reading List:** `02-lld-projects/snake-and-ladder/PROBLEM.md`
- **Coding Drills:**
  - Board initialization and dice roll simulation.

**Day 35: Phase 2 Assessment**
- Complete a 90-minute timed LLD mock on an unseen problem (e.g., Library Management).
- **Scorecard Rubric:** Adherence to SOLID, handling of edge cases, clear class diagrams.

---

## 📈 Scorecard Rubrics & Evaluation

During your self-assessments or mock interviews, evaluate yourself out of 5 for each category:

### LLD Rubric
1. **Requirement Gathering (0-5):** Asks clarifying questions, defines scope.
2. **Object-Oriented Design (0-5):** Identifies correct entities, relationships, uses patterns appropriately.
3. **Working Code (0-5):** Core logic is implemented, compiles mentally or actually, thread-safe if applicable.
4. **Code Quality (0-5):** Meaningful names, modularity, adherence to SOLID.
5. **Testing & Edge Cases (0-5):** Handles nulls, concurrency, boundaries.




---

## 📅 Phase 3: Weeks 6-7 - Distributed Systems & HLD

**Goal:** Understand core distributed systems concepts and apply them to high-frequency High-Level Design (HLD) interviews.

### Week 6: Distributed Systems Foundations

**Day 36-37: CAP Theorem, Consistency, & Caching**
- **Reading List:**
  - `03-hld-concepts/cap-theorem/THEORY.md`
  - `03-hld-concepts/database-isolation-levels/THEORY.md`
  - `03-hld-concepts/caching/THEORY.md`
- **Coding Drills:**
  - Implement an LRU cache or study the `04-hld-projects/distributed-cache/` project.

**Day 38-39: Load Balancing & Databases**
- **Reading List:**
  - `03-hld-concepts/load-balancing/THEORY.md`
  - `03-hld-concepts/sql-vs-nosql/THEORY.md`
  - `03-hld-concepts/database-sharding/THEORY.md`
- **System Design:** 
  - Compare PostgreSQL and MongoDB for different use cases.

**Day 40-41: High-Frequency HLD 1**
- **Reading List:**
  - `04-hld-projects/url-shortener/PROBLEM.md`
  - `04-hld-projects/pastebin/PROBLEM.md`
- **System Design:**
  - Design URL Shortener and Pastebin focusing on capacity estimation and storage design.

**Day 42: Review & Buffer**
- Review Week 6 concepts.

### Week 7: Advanced HLD

**Day 43-44: High-Frequency HLD 2 (Social Media & Feeds)**
- **Reading List:**
  - `04-hld-projects/news-feed/PROBLEM.md`
  - `04-hld-projects/social-graph-engine-tao/PROBLEM.md`
- **System Design:**
  - Design a News Feed system (fanout-on-read vs fanout-on-write).

**Day 45-46: High-Frequency HLD 3 (Streaming & Storage)**
- **Reading List:**
  - `04-hld-projects/video-streaming/PROBLEM.md`
  - `04-hld-projects/distributed-cloud-storage-s3/PROBLEM.md`
- **System Design:**
  - Design YouTube or Google Drive (block storage, metadata management).

**Day 47-48: High-Frequency HLD 4 (Location & E-commerce)**
- **Reading List:**
  - `04-hld-projects/nearby-friends/PROBLEM.md`
  - `04-hld-projects/ecommerce-backend/PROBLEM.md`
- **System Design:**
  - Spatial indexing (Quadtrees, Geohashes) and distributed transactions.

**Day 49: Phase 3 Assessment**
- **Scorecard Rubric (HLD):** Run through an HLD mock on a generic system like `04-hld-projects/metrics-monitoring/PROBLEM.md`.

---

## 📅 Phase 4: Week 8 - GenAI Systems

**Goal:** Master the fundamentals of LLMs, vector databases, and system design for AI-native applications.

**Day 50-51: GenAI Foundations & Vector Search**
- **Reading List:**
  - `06-genai-systems/00-concepts/vector-databases/`
  - `06-genai-systems/00-concepts/rag-architecture/`
- **Study:**
  - Understand embeddings and semantic search.

**Day 52-53: GenAI HLD Projects**
- **Reading List:**
  - `06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/`
  - `06-genai-systems/02-llm-hld-projects/document-qa-rag/`
- **System Design:**
  - Design a complete RAG system with chunking, indexing, and generation.

**Day 54: Advanced LLM Orchestration**
- **Reading List:**
  - `06-genai-systems/00-concepts/model-routing-orchestration/`
  - `06-genai-systems/00-concepts/llm-evaluation/`
- **System Design:**
  - Design an `06-genai-systems/02-llm-hld-projects/agentic-workflow-orchestrator/`.

**Day 55-56: Review & GenAI Mock**
- Complete any pending GenAI topics.
- **Scorecard Rubric (GenAI):** Assess knowledge of vector db scaling and prompt caching.

---

## 📅 Phase 5: Week 9 - Mock Interviews & Calibration

**Goal:** Polish your delivery and synthesize your behavioral, HLD, and LLD skills in realistic settings.

**Day 57: Behavioral Calibration**
- **Reading List:**
  - `resources/interview-tips/company-playbooks/README.md`
- **Action:**
  - Draft STAR stories (Situation, Task, Action, Result) for conflict resolution, leadership, and failure.

**Day 58: HLD Mock Interview**
- **Action:**
  - 45-minute timed mock interview with a peer or platform.
  - Grade against the HLD Rubric.

**Day 59: LLD / GenAI Mock Interview**
- **Action:**
  - 45-minute timed mock interview covering either a classic LLD or a GenAI component.

**Day 60: Final Calibration & Review**
- Review your scorecards.
- Identify weak spots for the final week before your actual interview.

---

### HLD Rubric
1. **Requirements & Scope (0-5):** Estimates scale (QPS, storage, bandwidth), defines APIs.
2. **High-Level Design (0-5):** Draws block diagrams, identifies core components.
3. **Deep Dive (0-5):** Explains trade-offs (SQL vs NoSQL, CP vs AP), handles bottlenecks.
4. **Data Models (0-5):** Database schema, sharding strategies, caching layers.
5. **Resiliency & Fault Tolerance (0-5):** Single points of failure, disaster recovery.

### GenAI System Rubric
1. **Model Selection & Cost (0-5):** Token estimation, prompt limits, LLM selection.
2. **Data Pipeline (0-5):** Embedding generation, chunking strategies, vector store design.
3. **Retrieval & Ranking (0-5):** Semantic vs hybrid search, reranking.
4. **Safety & Governance (0-5):** PII filtering, prompt injection defense, evaluation.

### Behavioral Rubric
1. **STAR Method (0-5):** Structured answers, focused on "I" not "We".
2. **Leadership Principles (0-5):** Demonstrates ownership, bias for action, delivering results.
3. **Clarity & Communication (0-5):** Clear articulation, handles follow-up questions well.
---

*Consistency is key. Stick to the daily plan, adjust your buffer days as needed, and good luck! 🚀*
