# Inventory Management — Interview Scoring Rubric

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements Clarity | 15% | Correct scope boundaries and assumptions |
| 2 | Entity Modeling | 25% | Clear `InventoryManager`/`Warehouse` split |
| 3 | Invariant Handling | 25% | No-negative-stock enforcement and transfer correctness |
| 4 | Extensibility | 20% | Pluggable alerting, clean API growth path |
| 5 | Concurrency & Communication | 15% | Thread-safe mutations and clear tradeoffs |

## Score Anchors

### 1 — Weak
- Missing invariants.
- Overloaded god-class design.
- No transfer correctness discussion.

### 3 — Acceptable
- Correct core entities and operations.
- Basic invariant checks.
- Mentions concurrency concerns.

### 5 — Strong
- Explicit invariants and failure contracts.
- Atomic transfer flow with deadlock-safe locking strategy.
- Alerting extension discussed without coupling core domain to transport.
