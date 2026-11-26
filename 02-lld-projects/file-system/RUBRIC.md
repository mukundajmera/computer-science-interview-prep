# File System — Interview Scoring Rubric

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements clarity | 15% | Correct scope for in-memory FS and path semantics |
| 2 | Entity modeling | 25% | Clean `FileSystem` / `Directory` / `FileSystemEntry` / `File` split |
| 3 | Tree operations correctness | 25% | Reliable create/delete/move/copy with parent-child consistency |
| 4 | Error handling and edge cases | 20% | Invalid paths, root rules, self-copy prevention |
| 5 | Extensibility and communication | 15% | Search/metadata/thread-safety extension strategy |

## Score Anchors

### 1 — Weak
- Blurs file vs directory responsibilities.
- Path resolution contracts are vague.
- Omits failure behavior.

### 3 — Acceptable
- Correct base entity model.
- Supports core operations with reasonable validation.
- Mentions complexity and edge cases.

### 5 — Strong
- Enforces invariants around tree structure and root behavior.
- Handles move/copy/search edge cases cleanly.
- Explains clear extension path for permissions/search/indexing/concurrency.
