# Evaluation Rubric

## 1. Core State Machine (30%)
- **L7 (Staff - Optional Failure Trace):** Formal verification or deep simulation of concurrent edge cases (e.g., clock skews in time-based windows, distributed state implications). Explicitly documents assumptions about OS thread scheduling.
- **L6 (Senior - Failure Trace):** Flawless implementation of CLOSED, OPEN, and HALF_OPEN states. Correct transition logic. Atomic state transitions using fine-grained locks or `AtomicReference`. 
- **L5 (Mid - Trade-offs):** Implements the core states correctly and discusses trade-offs between locking and atomic variables. Might have minor race conditions.
- **L4 (Beginner - Intuitive Minimum):** Basic state machine working but uses coarse-grained locks (e.g., `synchronized` on `execute`).

## 2. Metric Aggregation (30%)
- **L7 (Staff):** Implements zero-allocation, lock-free time-based windows or explicitly analyzes garbage collection pauses caused by bucket allocation.
- **L6 (Senior):** Efficient implementation of time-based sliding windows. Correctly calculates failure and slow call rates. Handles window sliding or eviction seamlessly using atomic updates (`AtomicInteger`/`LongAdder`).
- **L5 (Mid):** Implements count-based sliding window correctly. Discusses time-based window but implementation might have inefficiencies (e.g., iterating over the entire window on every call).
- **L4 (Beginner):** Simple list-based or circular array count-based window.

## 3. Concurrency and Thread Safety (20%)
- **L7 (Staff):** Mathematical or formal proof sketch of thread safety. Zero data races even under adversarial thread scheduling.
- **L6 (Senior):** Uses appropriate concurrency primitives (atomic variables). High throughput and minimal contention under heavy load.
- **L5 (Mid):** Thread-safe but uses coarse-grained locks, leading to potential bottlenecks. Discusses the trade-off.
- **L4 (Beginner):** Not fully thread-safe, leading to data corruption or lost updates in metrics under load.

## 4. Features & Extensibility (20%)
- **L7 (Staff):** Pluggable architecture. Custom exception predicates. Distributed state simulation.
- **L6 (Senior):** Supports slow call thresholds, fallback decorators, and custom configurations. Clean API design. Explicitly avoids recording its own fast-fail rejections as backend errors.
- **L5 (Mid):** Supports basic features. Mentions fallbacks but might tightly couple them to the core logic.
- **L4 (Beginner):** Hardcoded configurations, missing key features like fallbacks.
