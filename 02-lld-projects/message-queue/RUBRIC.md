# In-Memory Message Queue - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
| --- | --- | --- |
| Concurrency & Thread-safety | 30% | Correct use of locks/concurrent data structures, no race conditions. |
| Core Mechanics | 30% | Clear topic/partition/offset model. |
| DAG Execution | 20% | Correctly implements dependency ordering among subscribers. |
| Extensibility | 10% | Easy to plug in retry policies and routing. |
| Testing | 10% | Comprehensive tests covering multi-threading, DAG, retries. |

## Performance bands
- 1: Fails to implement basic queue.
- 2: Basic queue works but lacks partitions or thread safety.
- 3: Good queue with partitions, but DAG or retries have flaws.
- 4: Solid implementation of all features.
- 5: Exceptional code quality, clear abstractions, handles all edge cases gracefully.

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [DESIGN.md](./DESIGN.md)
