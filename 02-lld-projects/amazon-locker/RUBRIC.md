# Amazon Locker — Interview Scoring Rubric

## Scoring overview

| # | Dimension | Weight | Key signal |
|---|---|---|---|
| 1 | Requirements clarity | 15% | Correct scope and failure behavior |
| 2 | Entity modeling | 25% | Locker/token/compartment responsibilities |
| 3 | State correctness | 25% | Expiry, occupancy, and pickup transitions |
| 4 | Extensibility | 20% | Policy abstraction, reservation evolution |
| 5 | Communication and code quality | 15% | Deterministic, test-friendly design |

## Scale descriptors

| Score | Descriptor |
|---|---|
| **1 — Poor** | Blurry ownership, no clear token-expiry behavior, mutable ad-hoc logic. |
| **3 — Acceptable** | Correct baseline flows with clear error handling and valid entity boundaries. |
| **5 — Strong** | Clean policy/state abstractions, reservation extension path, deterministic testability. |
