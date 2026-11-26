# In-Memory Event Bus - Interview Scoring Rubric

## Acceptance Cases
| Level | Description | Requirement |
| --- | --- | --- |
| L4 (Minimum) | Intuitive minimum example | Correct core mechanics (Topic, Partition, Consumer Group). Implementation compiles and handles basic pub-sub functionality. Code demonstrates a basic understanding of concurrency using locks. |
| L5 (Trade-offs) | Trade-offs | Handles thread-safety robustly (`ReadWriteLock` / `ConcurrentHashMap`). Properly explains why specific concurrent data structures are chosen. Differentiates point-to-point and pub-sub. |
| L6/L7 (Advanced) | Optional failure trace with assumptions | Correctly simulates a failure trace involving retries and DLQ without deadlock. Clearly distinguishes the in-memory simulation from a distributed, deployed system (e.g., acknowledging lack of disk persistence or distributed consensus). |

## Scoring Dimensions
| Dimension | Weight | Strong signal |
| --- | --- | --- |
| Concurrency & Thread-safety | 30% | Correct use of locks/concurrent data structures, no race conditions or deadlocks. |
| Core Mechanics | 30% | Clear topic/partition/offset model reflecting actual event bus designs. |
| Retries & DLQ | 20% | Correctly implements retry and DLQ logic with safe state transitions. |
| Testing/Verification | 20% | Demonstrates understanding of how to verify concurrent access and retry states. |
