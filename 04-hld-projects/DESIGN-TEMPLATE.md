# 📋 HLD Design Template

Use this template as a framework for practicing system design interviews.

> **Evidence Contract Note:** This template adheres to the `curriculum-evidence-contract.md`. 
> Target Layer: [Beginner / Core / Staff] (Required)
> HLD designs remain docs-only unless an explicit policy exception is noted. Unsourced figures are scenario assumptions, not verified external facts.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: ___
- Core user value: ___

### Functional Requirements
- [ ] FR1: ___
- [ ] FR2: ___
- [ ] FR3: ___

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | ___ |
| Read latency | ___ |
| Write latency | ___ |
| Throughput | ___ |
| Consistency | ___ |
| Durability | ___ |

### Constraints
- Regulatory/compliance: ___
- Budget/cost preference: ___
- Team/operational constraints: ___
- Region/geography constraints: ___

### Out of Scope (Non-Goals)
- ___
- ___

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | ___ | input |
| Requests/user/day | ___ | input |
| Daily requests | ___ | DAU × requests/user |
| Avg QPS | ___ | daily / 86400 |
| Peak QPS | ___ | avg × burst factor |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| ___ | ___ | ___ | ___ |
| ___ | ___ | ___ | ___ |

### Decision Notes
- Which estimate forces a design choice? ___
- What assumption is most uncertain? ___

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: REST / gRPC / event / mixed
- Auth model: ___
- Rate limiting policy: ___

### Core Endpoints
```http
POST /api/v1/___
GET /api/v1/___?cursor=...&limit=...
PATCH /api/v1/___/{id}
```

### Error Model
- `400` invalid input
- `401/403` auth/authz
- `404` missing resource
- `409` conflict/concurrency
- `429` throttled
- `5xx` internal dependency failure

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- Entity A: ___
- Entity B: ___
- Entity C: ___

### Storage Choices
- Primary DB: ___ (reason: ___)
- Cache: ___ (reason: ___)
- Search index (if needed): ___
- Blob/object storage (if needed): ___

### Key Access Patterns
1. Read path query: ___
2. Write path mutation: ___
3. Secondary lookup: ___

### Partition and Index Notes
- Partition key: ___
- Hot key risk: ___
- Required indexes: ___

---

## 5. 🏗️ High-Level Architecture

### Component List
- API Gateway / Load Balancer
- Stateless app tier
- Data stores
- Async pipeline (if needed)
- Observability and control plane

### Read Path
1. ___
2. ___
3. ___

### Write Path
1. ___
2. ___
3. ___

### Explicit Traces

#### Normal Trace
1. ___
2. ___

#### Failure Trace
- Dependency timeout behavior: ___
- Retry policy + idempotency: ___
- Degraded mode / Network partition: ___

#### Evidence
- Verified metrics source: ___
- Testing/simulation contract: ___

---

## 6. 🔍 Deep Dives (Pick 1-2)

### Deep Dive A: ___
- Bottleneck: ___
- Chosen pattern: ___
- Alternative considered: ___
- Trade-off accepted: ___

### Deep Dive B: ___
- Consistency model: ___
- Scaling strategy: ___
- Failure handling: ___

---

## 7. 📈 Staff-Level Analysis (Optional)

*Note: This section is strictly optional and intended only for Staff-level layer content. It does not require a mandated 8-doc pack.*
- Complex failure domain interactions: ___
- Multi-region routing nuances: ___
- Security/compliance invariants: ___

---

## 8. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Data store | ___ | ___ | ___ | ___ |
| Caching strategy | ___ | ___ | ___ | ___ |
| Async model | ___ | ___ | ___ | ___ |

---

## 9. 🔮 Follow-up Questions

1. What changes at 10x scale?
2. What fails first under a regional outage?
3. How does the design change for strict consistency?
4. How do you reduce cloud cost by 30%?
5. How do you support multi-region rollout?

---

## 10. 🧩 Variants and Extensions

- Variant 1 (global users): ___
- Variant 2 (compliance-heavy): ___
- Variant 3 (realtime-first): ___
- Variant 4 (cost-optimized startup): ___

---

## 11. 🚨 Common Pitfalls (Self-Check)

- [ ] I skipped clarifying requirements
- [ ] I did estimates that did not influence design
- [ ] I added sharding/queueing without scale justification
- [ ] I did not mention failure handling
- [ ] I did not articulate trade-offs explicitly
- [ ] I left no time for summary

---

## 12. 🧮 Scoring Rubric (Self-Evaluation)

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) | Your Score |
|---|---|---|---|---|
| Requirements handling | Vague | Mostly clear | Prioritized + quantified | ___ |
| Architecture clarity | Boxes only | Basic flow | End-to-end + failure-aware | ___ |
| Technical depth | Tool names | Some rationale | Pattern + metric-driven rationale | ___ |
| Trade-off quality | None | Some | Explicit and contextual | ___ |
| Communication | Disorganized | Understandable | Structured + concise | ___ |

---

## 13. ✅ Wrap-up Summary (Final 60-90 Seconds)

Use this closing pattern:
1. Restate key requirements and constraints
2. Summarize core architecture choice
3. Call out one intentional trade-off
4. Mention one scale-evolution step

---

## 📌 Final Checklist

- [ ] Requirements and constraints captured
- [ ] Estimates tied to decisions
- [ ] APIs and entities are coherent
- [ ] Read/write paths are explicit
- [ ] Deep dive completed
- [ ] Trade-offs stated
- [ ] Follow-ups addressed
- [ ] Strong summary delivered
- [ ] Evidence fields mapped to sources/tests where applicable

---

*Copy this template for each system you practice!*

## 14. 🛑 Bottlenecks and Failure Modes

| Component | Failure Mode | Mitigation | Impact | Detection | Recovery |
|---|---|---|---|---|---|
| Component 1 | Failure A | Auto-scaling group | Brief latency spike | 5xx rate spikes | Auto-replace |
| Component 2 | Failure B | Drop idle connections | Clients must reconnect | Memory utilization alarm | Auto-restart |
| Component 3 | Failure C | Replicate across AZs | Increased publish latency | Consumer lag spikes | Failover to replica |
| Component 4 | Failure D | Cluster with replicas | Cache misses hit DB | Replication lag alarm | Auto-promote replica |
| Component 5 | Failure E | Quorum reads/writes | Minimal | Node heartbeat failure | Gossip protocol sync |
| Component 6 | Failure F | Backoff and retry queues | Delayed notifications | 429 response rate | Exponential backoff |

## 15. 📈 Scaling Stages

- **10K Users**: Single monolith, simple DB, basic caching.
- **1M Users**: Microservices, robust cache, read replicas.
- **100M+ Users**: Sharded databases, globally distributed edge nodes, event streaming.
