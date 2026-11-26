# Connect Four — Interview Scoring Rubric

## Scoring overview

| # | Dimension | Weight | Key signal |
|---|---|---|---|
| 1 | Requirements clarity | 15% | Correct scope, error handling, and out-of-scope boundaries |
| 2 | Entity modeling | 25% | Clean `Game` vs `Board` separation |
| 3 | Rule correctness | 25% | Gravity + win/draw detection correctness |
| 4 | Extensibility | 20% | Undo/bot evolution without rewrites |
| 5 | Communication and code quality | 15% | Deterministic APIs, readable flow |

## Scale descriptors

| Score | Descriptor |
|---|---|
| **1 — Poor** | Blends all logic into one class, misses core invalid-move cases, no clear terminal-state handling. |
| **3 — Acceptable** | Correctly models board/game/player, detects wins, handles major validation paths. |
| **5 — Strong** | Explains trade-offs, supports undo cleanly, introduces pluggable bot strategy, and defends invariants. |
