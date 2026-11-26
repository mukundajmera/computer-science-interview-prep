# Collaborative Document Editor — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Correctly scopes collaboration behaviors |
| 2 | Estimation | 10% | Websocket/session assumptions drive design |
| 3 | API Design | 15% | Metadata + realtime protocol separation |
| 4 | Data Model | 15% | Operation/snapshot/session model clarity |
| 5 | Architecture | 20% | Session routing + transform + persistence flow |
| 6 | Deep Dives | 20% | Convergence, scaling, replay recovery |
| 7 | Trade-offs & Communication | 10% | Clear consistency and durability rationale |

## Dimension Signals (1 / 3 / 5)

### 1. Requirements
- **1:** Generic CRUD framing only.
- **3:** Captures multi-user editing and realtime updates.
- **5:** Explicit convergence and session constraints with boundaries.

### 2. Estimation
- **1:** No connection/operation assumptions.
- **3:** Rough concurrency estimates.
- **5:** Estimates that influence routing and snapshot strategy.

### 3. API Design
- **1:** No realtime contract.
- **3:** Basic REST and websocket endpoint.
- **5:** Operation frame semantics, replay token, and error handling defined.

### 4. Data Model
- **1:** Only full-document blobs.
- **3:** Document + operation entities.
- **5:** Includes versioning, session presence, and compaction model.

### 5. Architecture
- **1:** Single server reasoning.
- **3:** Service split.
- **5:** Correct data path for edit, broadcast, replay, and snapshot persistence.

### 6. Deep Dives
- **1:** No concurrency conflict handling.
- **3:** Mentions OT/CRDT conceptually.
- **5:** Explains transform/rebase flow and reconnect recovery.

### 7. Trade-offs & Communication
- **1:** No rationale.
- **3:** Mentions alternatives.
- **5:** Chooses consistency and latency posture with explicit constraints.
