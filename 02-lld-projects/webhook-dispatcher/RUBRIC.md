# Webhook Dispatcher - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
| --- | --- | --- |
| Concurrency Control | 30% | Correctly uses per-destination semaphores to throttle concurrent requests without deadlocks. |
| Retry & Backoff | 25% | Implements exponential backoff with full jitter accurately. Handles exhausted retries via DLQ. |
| Security | 15% | Correctly implements RFC 2104 HMAC-SHA256 and includes it in headers. |
| Async Dispatch | 15% | Properly uses a worker pool/executor service for non-blocking dispatch. |
| Code Quality | 15% | Clean models, separation of concerns, and thread-safe data structures. |

## Performance bands
- **Strong Hire:** Implements all core capabilities robustly, uses appropriate concurrency primitives, and includes solid test coverage for edge cases like jitter and DLQ.
- **Hire:** Implements the happy path and basic retries, but might miss full jitter or have minor concurrency inefficiencies.
- **No Hire:** Blocks the main thread for dispatch, lacks concurrency controls, or fails to implement HMAC properly.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
