# Code Walkthrough: Online Code Judge

This document outlines the entry APIs, version progression, correctness invariants, and algorithmic complexity of the Online Code Judge simulation.
Note: The system implements only a trusted fake execution-adapter simulation of submissions/verdicts. It does not execute user-supplied code on the host. MLE and TLE are adapter-reported simulations, not unproven isolation.

## Entry APIs
- `submit(Submission)`: Accepts a user submission and enqueues it for processing.
- `getVerdict(submissionId)` (Java) or `get_verdict(submission_id)` (Python): Returns the current verdict (e.g., PENDING, AC, WA, TLE, MLE) of a submission.

## Version Delta Table

| Version | Directory | Description |
|---|---|---|
| `v1-basic` | `java/v1-basic/`, `python/v1-basic/` | Synchronous evaluation loop blocking the caller thread. |
| `v2-extended` | `java/v2-extended/`, `python/v2-extended/` | Strategy Pattern introduced via `LanguageRunner` interface (or Python equivalent) for cleanly decoupling execution logic. |
| `v3-optimized` | `java/v3-optimized/`, `python/v3-optimized/` | Producer-Consumer asynchronous architecture using thread-safe queues and background worker pools. |

## Correctness Invariants
- **Fast-fail Evaluation:** Test cases immediately halt on the first non-AC verdict (WA, TLE, MLE, RE) to conserve resources.
- **Atomic State Transitions:** In `v3-optimized`, concurrent data structures (`ConcurrentHashMap` in Java, locks in Python) ensure submission verdicts are visible without read-write race conditions.
- **Resource Constraints (Simulated):** Time taken limits strictly yields TLE, and memory used > `memoryLimitKb` strictly yields MLE.

## Algorithmic Complexity
- **Submission Enqueue:** $O(1)$ time complexity using `LinkedBlockingQueue` (Java) or `queue.Queue` (Python).
- **Verdict Lookup:** $O(1)$ expected time complexity via hash map lookups.
- **Evaluation:** $O(T)$ where $T$ is the number of test cases, bounded by early termination on failure.
