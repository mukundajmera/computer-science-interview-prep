# Rideshare Matching Engine - Interview Scoring Rubric

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Design Document](DESIGN.md)

## Scoring rubric

| Dimension | Weight | Strong signal |
| :--- | :---: | :--- |
| **State Machine FSM** | 25% | Encapsulates state transitions cleanly inside the Driver/Trip model. Ensures invalid transitions (e.g., IDLE -> COMPLETED) are safely rejected without exception bloat. |
| **Concurrency & Safety** | 35% | Protects driver allocation with a fine-grained locking mechanism (RLock/ReentrantLock). Prevents double assignment without unnecessarily blocking the entire MatchingEngine globally. |
| **Spatial Calculation** | 20% | Correctly identifies and sorts idle drivers via Euclidean or Haversine distances. Understands the difference between naive iteration and spatial indices (e.g., quad trees). |
| **Pricing Engine Strategy** | 20% | Threads safe supply/demand updates properly. Keeps logic separated from the matching orchestration. Evaluates edge cases (division by zero, negative capacity). |

## Performance bands

- **Strong Hire**: Implements all features fully thread-safe. Avoids deadlocks by not locking the global `MatchingEngine` while locking a driver or trip. Code is clean and modular. Tests cover concurrent thread race conditions perfectly.
- **Hire**: Completes most functionality. Might use slightly less optimal locking (e.g., locking the entire engine to assign a trip instead of individual driver locks). Understands state machine patterns.
- **No Hire**: Fails to understand or handle concurrent requests (resulting in duplicate trip assignments to a single driver). Does not accurately implement FSM logic or the spatial sorting algorithm.
