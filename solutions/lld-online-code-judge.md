# Coach Answer: Online Code Judge

## ⏱️ 45-Minute Pacing Target

1. **Requirements & Scope (5 mins):** Align on languages supported, verdicts (AC, WA, TLE, MLE, CE), and resource limits.
2. **Entity Modeling (10 mins):** Define `Problem`, `Submission`, `TestCase`, `Verdict`.
3. **Core Logic (15 mins):** Implement the evaluation loop and Strategy Pattern for `LanguageRunner`.
4. **Concurrency (10 mins):** Implement the Producer-Consumer queue for asynchronous evaluation.
5. **Trade-offs (5 mins):** Discuss sandbox isolation and distributed queueing.

## 🗣️ Interview Script

### 1. Requirements Gathering
**Say:** "Our judge must handle asynchronous submissions, execute them against test cases with time and memory limits, and support multiple languages. I'll design it to be easily extensible using design patterns and ensure thread-safety for concurrent submissions."

### 2. Entity Modeling & Design Patterns
**Say:** "I'll use the **Strategy Pattern** for the language runners. A `LanguageRunner` interface will have implementations like `PythonRunner` and `JavaRunner`. This makes adding a new language like Go or C++ trivial without modifying the core `CodeJudge` logic."

### 3. Thread-Safety & Queueing
**Say:** "To prevent blocking the main thread, I'll use a **Producer-Consumer** pattern. Incoming submissions go into a thread-safe `BlockingQueue`. A fixed pool of worker threads will continuously pull from this queue. For fast lookups of verdicts, I'll use a `ConcurrentHashMap`."

### 4. Code Structure
(Refer to the v3-optimized implementation for the ideal code layout).
Ensure you highlight the early exit logic: if a test case fails, immediately break out of the loop and return the failing verdict to save compute cycles.

### 5. Follow-ups
**Say:** "In a real production environment, we wouldn't run user code directly on the host machine. We would use Docker containers or Firecracker microVMs for strong security isolation. We would also replace the in-memory queue with Kafka to scale the executors independently of the web tier."
