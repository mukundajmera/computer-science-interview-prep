# In-Memory Multi-Policy Cache - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
| :--- | :--- | :--- |
| Core Requirements | 25% | Candidate correctly implements cache core logic with generic types, bounds, and strategy delegation. Handles TTL edge cases appropriately. |
| O(1) LFU Design | 25% | Implements LFU optimally using a Frequency Node map with doubly linked lists, avoiding O(N) or O(log N) tree/heap sorts. |
| Runtime Strategy Swap | 20% | Candidate handles strategy swapping smoothly by re-ordering metadata attributes to preserve valid eviction tracking state during transition. |
| Concurrency Model | 20% | Safely implements `ReentrantReadWriteLock` / `RLock`. Active TTL worker thread gracefully halts on shutdown and handles lock acquisition safely. |
| Code Organization | 10% | Clean object-oriented design using Strategy patterns. Methods are small, testable, and adhere to SRP. |

## Performance bands

- **Strong Hire:** Implements LFU correctly in O(1) time. Policy swapping reconstructs state logically based on historical timestamps. Lock granularity avoids deadlocks and race conditions. Clean separation of concerns via Strategy pattern.
- **Hire:** Functional multi-policy cache. May use O(log N) structures for LFU (e.g., Min-Heap or TreeMap). Swapping works but might rebuild state inefficiently. Basic thread safety with coarse locks.
- **No Hire:** Struggles with O(1) linked list pointer manipulation. Fails to provide thread safety. Background threads cause concurrent modification exceptions. Hardcodes strategies without patterns.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
