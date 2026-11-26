# 📚 90-Day Study Plan (Staff, Principal & Architect)

A rigorous 12-13 week plan (~18 hrs/week) tailored specifically for Staff, Principal, and Architect candidates. At this level, expectations shift from component-level design to system-wide architecture, organizational leadership, and deep technical trade-offs. This plan focuses intensely on distributed consensus, storage internals, complex data pipelines, and architectural defense.

---

## 📋 Overview

| Phase | Weeks | Focus Area | Expected Hours |
|-------|-------|------------|----------------|
| **Phase 1** | Weeks 1-2 | Distributed Systems Theory & Consensus | ~18 hrs/week |
| **Phase 2** | Weeks 3-4 | Storage Internals & Data Replication | ~18 hrs/week |
| **Phase 3** | Weeks 5-6 | Complex Transactions & Sagas | ~18 hrs/week |
| **Phase 4** | Weeks 7-8 | Streaming, Data Pipelines & EOS | ~18 hrs/week |
| **Phase 5** | Weeks 9-10 | Architecture Review & Org Leadership | ~18 hrs/week |
| **Phase 6** | Weeks 11-12 | AI-Native Architecture & GenAI Guardrails | ~18 hrs/week |
| **Phase 7** | Week 13 | Final Polish & Mock Interviews | ~18 hrs/week |

**Total Time:** ~230 hours over 13 weeks

---

## 📅 Phase 1: Weeks 1-2 - Distributed Systems Theory & Consensus

**Goal:** Deepen understanding of how distributed systems achieve agreement, handle network partitions, and maintain consistency at scale.

### Week 1: Core Theory & Time in Distributed Systems

**Day 1-2: CAP, PACELC, & Consistency spectrum**
- **Reading List:**
  - `00-theory/system-design-fundamentals/cap-theorem.md`
  - `00-theory/distributed-systems/consistency-models.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Write a 1-page summary contrasting Linearizability vs Sequential Consistency vs Causal Consistency.

**Day 3-4: Logical Clocks & Ordering**
- **Reading List:**
  - `00-theory/distributed-systems/vector-clocks.md` (Coming Soon 🔜)
  - External Reading: Lamport Clocks, Vector Clocks, TrueTime (Spanner).
- **Milestone Deliverable:** Design a conflict resolution mechanism for a collaborative text editor using Vector Clocks.

**Day 5-6: Consensus Protocols - Paxos**
- **Reading List:**
  - `00-theory/distributed-systems/paxos.md` (Coming Soon 🔜)
  - External Reading: "Paxos Made Simple" by Leslie Lamport.
- **Milestone Deliverable:** Explain the Basic Paxos flow (Prepare, Promise, Accept, Accepted) to a peer.

**Day 7: Buffer & Review**

### Week 2: Modern Consensus & Coordination

**Day 8-9: Consensus Protocols - Raft**
- **Reading List:**
  - `00-theory/distributed-systems/raft.md` (Coming Soon 🔜)
  - External Reading: "In Search of an Understandable Consensus Algorithm".
- **Milestone Deliverable:** Compare Leader Election and Log Replication in Raft vs Paxos.

**Day 10-11: Coordination Services (ZooKeeper / etcd)**
- **Reading List:**
  - `00-theory/distributed-systems/zookeeper.md` (Coming Soon 🔜)
  - `00-theory/distributed-systems/etcd.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design a distributed lock manager using ZooKeeper's ephemeral nodes.

**Day 12-13: Gossip Protocols & Failure Detection**
- **Reading List:**
  - `00-theory/distributed-systems/gossip-protocol.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Analyze the trade-offs of using Phi Accrual Failure Detector in a 10,000-node cluster.

**Day 14: Phase 1 Assessment**
- **Scenario Simulation:** Defend the choice of Raft vs Gossip for managing metadata in a globally distributed storage system.
- **Roles:** You (Architecture Lead), Peer (Storage Team Lead), Peer (Product Manager).
- **Trade-offs:** Strong consistency (higher latency) vs Eventual consistency (faster writes).
- **Debrief Rubric:**
  - **Architecture Design (0-5):** Did you accurately evaluate the use cases for Raft and Gossip?
  - **Trade-off Analysis (0-5):** Did you clearly explain the impact of consistency choices?
  - **Scalability (0-5):** Did you address the scalability limits of each protocol?
  - **Communication (0-5):** Did you effectively justify your decision to non-technical stakeholders?

---

## 📅 Phase 2: Weeks 3-4 - Storage Internals & Data Replication

**Goal:** Understand how databases store data on disk and replicate it across networks. A Staff engineer must know database internals to optimize for specific workloads.

### Week 3: Storage Engines

**Day 15-16: B-Trees & B+Trees**
- **Reading List:**
  - `00-theory/databases/b-trees.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Calculate the depth of a B+Tree given a specific page size, key size, and billion-row dataset.

**Day 17-19: Log-Structured Merge (LSM) Trees & SSTables**
- **Reading List:**
  - `00-theory/databases/lsm-trees.md` (Coming Soon 🔜)
  - External Reading: LevelDB / RocksDB architecture.
- **Milestone Deliverable:** Explain Write Amplification, Read Amplification, and Space Amplification in LSM trees.

**Day 20-21: Columnar Storage & Data Warehouses**
- **Reading List:**
  - `00-theory/databases/columnar-databases.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design an analytics pipeline utilizing Parquet files and an OLAP engine.

### Week 4: Replication & Partitioning

**Day 22-23: Leader-based vs Leaderless Replication**
- **Reading List:**
  - `00-theory/database-concepts/replication.md`
  - External Reading: Dynamo: Amazon's Highly Available Key-value Store.
- **Milestone Deliverable:** Map Dynamo's Quorum (N, W, R) configurations to different consistency/availability needs.

**Day 24-25: Multi-Region Active-Active Architectures**
- **Reading List:**
  - `00-theory/databases/multi-region.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design a multi-region user profile service handling split-brain scenarios and conflict resolution (e.g., CRDTs).

**Day 26-27: Advanced Sharding Strategies**
- **Reading List:**
  - `00-theory/database-concepts/sharding.md`
- **Milestone Deliverable:** Propose a seamless resharding (rebalancing) strategy for a database that has reached its capacity limit without downtime.

**Day 28: Phase 2 Assessment**
- **Scenario Simulation:** Debug a severe latency spike in a Cassandra cluster during a read-heavy workload.
- **Roles:** You (Incident Commander), Peer (Site Reliability Engineer), Peer (Customer Support Lead).
- **Trade-offs:** Fast recovery (data loss risk) vs exact state restoration (high MTTR).
- **Debrief Rubric:**
  - **Triage & Mitigation (0-5):** Did you rapidly isolate the fault domain and stop the bleeding?
  - **Root Cause Analysis (0-5):** Did you correctly identify the underlying bottleneck or bug?
  - **Trade-off Analysis (0-5):** Did you clearly explain the impact of your mitigation strategy?
  - **Communication (0-5):** Did you provide clear updates to stakeholders?

---

## 📅 Phase 3: Weeks 5-6 - Complex Transactions & Sagas

**Goal:** Master distributed transactions in microservices architectures where ACID properties cannot be enforced by a single database.

### Week 5: Distributed Transactions

**Day 29-30: Two-Phase Commit (2PC) & Three-Phase Commit (3PC)**
- **Reading List:**
  - `00-theory/distributed-systems/2pc-3pc.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Identify the blocking problems in 2PC and how 3PC attempts to solve them (and why it still fails in network partitions).

**Day 31-33: The Saga Pattern**
- **Reading List:**
  - `00-theory/microservices/saga-pattern.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design a distributed order fulfillment process (Order -> Payment -> Inventory -> Shipping) using Choreography vs Orchestration.

**Day 34-35: Outbox Pattern & Change Data Capture (CDC)**
- **Reading List:**
  - `00-theory/microservices/outbox-pattern.md` (Coming Soon 🔜)
  - `00-theory/databases/cdc.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Architect a reliable messaging system using Debezium (CDC) and the Outbox pattern to prevent dual-write failures.

### Week 6: Idempotency & Resiliency

**Day 36-37: Designing Idempotent APIs**
- **Reading List:**
  - `00-theory/api-design/idempotency.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Create an API contract for a payment gateway utilizing Idempotency Keys and explain the lifecycle of a key.

**Day 38-40: Circuit Breakers, Bulkheads, & Rate Limiting**
- **Reading List:**
  - `00-theory/resiliency/circuit-breaker.md` (Coming Soon 🔜)
  - `06-genai-systems/README.md`
- **Milestone Deliverable:** Define the configuration parameters (failure threshold, reset timeout) for a Circuit Breaker protecting a critical downstream payment service.

**Day 41-42: Phase 3 Assessment**
- **Scenario Simulation:** Architect a resilient ticket booking system that handles massive concurrent traffic (e.g., Taylor Swift tour) preventing overselling and ensuring eventual consistency.
- **Roles:** You (Principal Engineer), Peer (Payment Gateway Lead), Peer (Load Testing Engineer).
- **Trade-offs:** Immediate consistency (locking bottleneck) vs Eventual consistency (overselling risk).
- **Debrief Rubric:**
  - **System Design (0-5):** Did you effectively use caching, queues, and rate limiting?
  - **Concurrency Handling (0-5):** Did you prevent overselling while maintaining high throughput?
  - **Trade-off Analysis (0-5):** Did you balance user experience with system reliability?
  - **Resiliency (0-5):** Did you design appropriate circuit breakers and fallbacks?

---

---

## 📅 Phase 4: Weeks 7-8 - Streaming, Data Pipelines & EOS

**Goal:** Deep dive into streaming architectures, exactly-once processing (EOS), and real-time data pipelines at scale.

### Week 7: Event Streaming & Message Brokers

**Day 43-44: Kafka Architecture & Storage Internals**
- **Reading List:**
  - `00-theory/distributed-systems/kafka-storage-internals.md`
- **Milestone Deliverable:** Diagram Kafka's partition replication, leader election, and segment file structure.

**Day 45-47: Exactly-Once Semantics (EOS) in Streaming**
- **Reading List:**
  - `00-theory/distributed-systems/exactly-once-semantics.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Write a design doc explaining how transactional IDs and producer epochs enable EOS in Kafka.

**Day 48-49: Real-time Data Pipelines & Stream Processing**
- **Reading List:**
  - `00-theory/data-engineering/stream-processing-frameworks.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design a real-time fraud detection pipeline using Flink and Kafka.

### Week 8: Advanced Streaming & Phase 4 Assessment

**Day 50-52: Lambda vs Kappa Architectures**
- **Reading List:**
  - `00-theory/data-engineering/lambda-vs-kappa.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Compare the operational overhead of Lambda vs Kappa for a billion-event-per-day analytics platform.

**Day 53-54: Handling Out-of-Order Events & Watermarks**
- **Reading List:**
  - `00-theory/data-engineering/event-time-and-watermarks.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Implement (pseudocode) a tumbling window aggregator that handles late-arriving events using watermarks.

**Day 55-56: Phase 4 Assessment**
- **Scenario Simulation:** Debug a severe lag in a consumer group processing payment events, where late events are causing incorrect aggregations.
- **Roles:** You (Data Architect), Peer (Streaming Engineer), Peer (Business Stakeholder).
- **Trade-offs:** Dropping late data (accuracy loss) vs buffering indefinitely (OOM risk/latency).
- **Debrief Rubric:**
  - **Architecture Design (0-5):** Did you accurately diagnose the partition imbalance or processing bottleneck?
  - **Trade-off Analysis (0-5):** Did you clearly explain the impact of watermark tuning?
  - **Resiliency (0-5):** Did you propose a robust dead-letter queue strategy for malformed events?
  - **Communication (0-5):** Did you provide clear updates on data correctness to stakeholders?

---

## 📅 Phase 5: Weeks 9-10 - Architecture Review & Organizational Leadership

**Goal:** Transition from designing systems to defending them, influencing roadmaps, and leading large engineering organizations.

### Week 9: Architecture Defense & Trade-offs

**Day 57-58: The Architecture Review Board (ARB)**
- **Reading List:**
  - `resources/interview-tips/architecture-review-defense.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Prepare a 2-page pre-read document for an ARB defending a migration from a monolith to microservices.

**Day 59-61: Cost Optimization & Capacity Planning**
- **Reading List:**
  - `resources/interview-tips/capacity-planning-and-cost.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Create a cost-model for a multi-petabyte storage system comparing AWS S3, Glacier, and custom on-prem solutions.

**Day 62-63: Build vs. Buy Decisions**
- **Reading List:**
  - `resources/interview-tips/build-vs-buy.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Evaluate whether to use managed Kafka (Confluent Cloud) or self-hosted Kafka for a team of 10 engineers.

### Week 10: Organizational Leadership

**Day 64-66: Engineering Strategy & Roadmapping**
- **Reading List:**
  - `resources/interview-tips/engineering-strategy.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Draft a 6-month technical roadmap to deprecate a legacy billing system without disrupting revenue.

**Day 67-68: Mentorship, Culture, & Conflict Resolution**
- **Reading List:**
  - `resources/interview-tips/staff-engineer-archetypes.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Write a STAR response for a time you resolved a deep technical disagreement between two senior engineers.

**Day 69-70: Phase 5 Assessment**
- **Scenario Simulation:** Present and defend an architectural proposal to unify two disparate user identity systems after a company acquisition.
- **Roles:** You (Principal Engineer), Peer (CTO), Peer (Security Lead).
- **Trade-offs:** Fast integration (technical debt/security risk) vs complete rewrite (delayed product features).
- **Debrief Rubric:**
  - **Strategic Vision (0-5):** Did the proposal align with long-term business goals?
  - **Trade-off Analysis (0-5):** Were the risks of both approaches clearly quantified?
  - **Leadership & Influence (0-5):** Did you effectively navigate pushback from the CTO?
  - **Security (0-5):** Did you adequately address the Security Lead's concerns regarding data migration?

---

## 📅 Phase 6: Weeks 11-12 - AI-Native Architecture & GenAI Guardrails

**Goal:** Design systems that integrate Large Language Models (LLMs) safely, reliably, and cost-effectively at scale.

### Week 11: GenAI Systems & RAG Architecture

**Day 71-73: Advanced RAG & Vector Databases**
- **Reading List:**
  - `06-genai-systems/00-concepts/rag-architecture/README.md`
  - `06-genai-systems/00-concepts/vector-databases/README.md`
- **Milestone Deliverable:** Design a multi-tenant RAG architecture that guarantees data isolation between enterprise clients.

**Day 74-75: LLM Routing, Caching & Cost Optimization**
- **Reading List:**
  - `06-genai-systems/00-concepts/model-routing-orchestration/README.md`
- **Milestone Deliverable:** Architect a prompt caching layer using Redis to reduce OpenAI API costs by 40%.

**Day 76-77: Agentic Workflows & Tool Use**
- **Reading List:**
  - `06-genai-systems/02-llm-hld-projects/agentic-workflow-orchestrator/README.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design the state management system for an autonomous coding agent that requires multi-step planning and execution.

### Week 12: GenAI Guardrails & Phase 6 Assessment

**Day 78-79: GenAI Guardrails & Prompt Injection Defense**
- **Reading List:**
  - `06-genai-systems/00-concepts/genai-security-guardrails.md` (Coming Soon 🔜)
- **Milestone Deliverable:** Design a defense-in-depth pipeline (input sanitization, output evaluation) to prevent malicious prompt injection in a customer-facing chatbot.

**Day 80-82: LLM Evaluation & Observability**
- **Reading List:**
  - `06-genai-systems/00-concepts/llm-evaluation/README.md`
- **Milestone Deliverable:** Define the golden dataset and automated metrics (e.g., faithfulness, answer relevance) for a legal document summarization system.

**Day 83-84: Phase 6 Assessment**
- **Scenario Simulation:** Respond to a critical incident where a customer-facing support LLM is leaking PII and hallucinating company policies.
- **Roles:** You (AI Architect), Peer (Legal Counsel), Peer (VP of Product).
- **Trade-offs:** Immediate shutdown (support overload) vs deploying quick-fix filters (risk of bypassing).
- **Debrief Rubric:**
  - **Triage & Mitigation (0-5):** Did you rapidly implement safeguards to stop the leak?
  - **Root Cause Analysis (0-5):** Did you identify the failure in the guardrail pipeline?
  - **Trade-off Analysis (0-5):** Did you clearly explain the impact of the mitigation to Product and Legal?
  - **Communication (0-5):** Did you maintain calm and provide actionable updates?

---

## 📅 Phase 7: Week 13 - Final Polish & Mock Interviews

**Goal:** Synthesize everything. Calibrate your performance under realistic interview pressure.

### Week 13: Mock Interviews and Calibration

**Day 85-87: HLD & Architecture Mock Interviews**
- **Action:**
  - Complete two 60-minute mock interviews focusing on complex distributed systems (e.g., Multi-Region Active-Active architectures, Sagas, Global Payment Gateway, Real-time Ad Exchange).
- **Milestone Deliverable:** Grade yourself against the Distributed Systems Architecture Rubric.

**Day 88-89: Behavioral & Leadership Calibration**
- **Action:**
  - Refine your "Most Complex Project" and "Organizational Impact" STAR stories.
- **Milestone Deliverable:** Deliver a 10-minute presentation on a past architectural failure and the lessons learned.

**Day 90: Final Review & Rest**
- **Action:**
  - Review cheat sheets, rest, and prepare mentally for the interview loop.

---

### Phase 4-7 Scorecard Highlights

**Architecture Review Rubric:**
1. **Strategic Alignment (0-5):** Does the design solve the business problem at the right cost?
2. **Defensibility (0-5):** Are trade-offs explicitly stated and well-justified?
3. **Completeness (0-5):** Are edge cases, migrations, and operability addressed?

**GenAI Systems Rubric:**
1. **Model & Cost Strategy (0-5):** Effective routing, caching, and token management.
2. **Data & Retrieval (0-5):** Robust vector search, chunking, and ranking.
3. **Safety & Guardrails (0-5):** Strong defenses against injection, hallucination, and data leaks.

---

*Consistency, depth, and the ability to articulate trade-offs are your strongest assets. Good luck! 🚀*
