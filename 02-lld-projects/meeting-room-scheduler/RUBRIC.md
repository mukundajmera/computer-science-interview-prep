# Meeting Room Scheduler - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
| --- | --- | --- |
| **Requirements Gathering** | 10% | Identifies constraints like interval mechanics `[start, end)` and concurrency. |
| **Entity Design** | 20% | Clean separation of `MeetingRoom`, `Meeting`, `Interval`, and `User`. |
| **Interval Math** | 20% | Correctly implements overlap logic `(s1 < e2 && s2 < e1)` without off-by-one errors. |
| **Concurrency & Thread Safety** | 30% | Protects room booking with fine-grained locking or synchronization. Avoids global locks. |
| **Extensibility (Patterns)** | 20% | Uses Strategy for allocation and Observer for notifications. |

## Performance bands
- **Strong Hire**: Implements thread-safe booking, correct interval overlap, and clean patterns within 45 mins.
- **Hire**: Working code with minor bugs in interval logic or sub-optimal locking (e.g., global lock).
- **No Hire**: Fails to prevent double booking or incorrect interval collision logic.

## Cross-links
- [Problem Description](PROBLEM.md)
- [Design Document](DESIGN.md)
