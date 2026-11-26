# Distributed Cache — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Correctly scopes cache role and guarantees |
| 2 | Estimation | 10% | Node sizing from memory + throughput |
| 3 | API Design | 15% | Coherent get/set/delete + TTL semantics |
| 4 | Data Model | 15% | Entry lifecycle and membership modeling |
| 5 | Architecture | 20% | Routing, replication, and rebalance clarity |
| 6 | Deep Dives | 20% | Hot keys, failover, latency control |
| 7 | Trade-offs & Communication | 10% | Explicit consistency/latency/cost rationale |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** Treats cache as durable database.
- **3:** Captures basic cache operations and latency.
- **5:** Defines durability/consistency boundaries and fallback behavior.

### 2. Estimation
- **1:** No sizing math.
- **3:** Rough node count estimate.
- **5:** Uses max(memory-based, throughput-based) sizing and safety margin.

### 3. API Design
- **1:** No TTL semantics.
- **3:** Basic operations listed.
- **5:** Clear TTL, error behavior, and idempotent delete semantics.

### 4. Data Model
- **1:** Key/value only.
- **3:** Includes expiry metadata.
- **5:** Adds membership and assignment metadata for operations and recovery.

### 5. Architecture
- **1:** Single node only.
- **3:** Clustered nodes with simple replication.
- **5:** Membership-aware routing + controlled rebalance strategy.

### 6. Deep Dives
- **1:** No hotspot/failure treatment.
- **3:** Mentions hot keys and failover.
- **5:** Concrete mitigation strategies and triggers.

### 7. Trade-offs & Communication
- **1:** No alternatives discussed.
- **3:** Basic pros/cons mentioned.
- **5:** Contextual decisions tied to SLA and cost profile.
