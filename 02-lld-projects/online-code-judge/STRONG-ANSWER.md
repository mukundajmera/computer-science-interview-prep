# Strong Answer: Online Code Judge

## Verbal Pacing Target (45 Minutes)
- **00-05 mins:** Clarifying Requirements & Scoping. Acknowledge this is a trusted fake execution-adapter simulation, not a real sandbox.
- **05-15 mins:** Entity Modeling & Strategy Pattern (Problem, Submission, Verdict, LanguageRunner).
- **15-30 mins:** Core Execution Logic & Concurrency Design (Producer-Consumer, Thread Safety in `v3-optimized`).
- **30-40 mins:** Correctness Invariants (Fast-fail Evaluation) & Complexity.
- **40-45 mins:** Production Trade-offs, Failure Traces & Review (VM/container isolation bounds).

## 1. Entity Modeling & Strategy Pattern

**Say:** "I will start by defining the core entities: `Submission`, `Problem`, `TestCase`, and a `Verdict` enum. To support multiple languages cleanly, I'll employ the Strategy Pattern with a `LanguageRunner` interface. Our simulated execution adapters will return TLE/MLE verdicts based on fake runtimes, rather than executing arbitrary files on the host."

## 2. Data Structure Rationale & Indexing Trade-offs

**Say:** "For local simulations, I'll use a `ConcurrentHashMap` to store submissions. This provides fast $O(1)$ lookups for the API. In a distributed environment, this would be replaced with an indexed database table (e.g., indexed by user and problem IDs)."

## 3. Concurrency Defense & State Synchronization

**Say:** "To avoid synchronous blocking, I will use a Producer-Consumer pattern. Submissions are enqueued into a thread-safe queue. Background worker threads poll this queue. Thread-safe maps ensure that updating a verdict from `PENDING` to `AC` is atomic and visible to callers without race conditions."

## 4. Failure Handling, VM Isolation, & Production Trade-offs

**Say:** "We must fast-fail evaluations: if a test case yields `WA` or `TLE`, we immediately halt execution of subsequent cases. 
Furthermore, while this implementation simulates MLE and TLE via adapter reports, standard library timeouts are not a security sandbox. In production, we require a separately approved VM/container boundary (like Firecracker) with strict filesystem, network, CPU, memory, output, and process controls."
