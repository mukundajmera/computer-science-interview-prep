# Approach: Online Code Judge

## 1. Core Entities
1. **Submission**: Represents a user's code submission, tracking its status, language, code, and final verdict.
2. **Problem**: Stores problem metadata including time limits, memory limits, and the list of test cases.
3. **TestCase**: A simple struct containing the input string and the expected output string.
4. **Verdict**: An enumeration of possible execution outcomes (AC, WA, TLE, MLE, CE, PENDING).
5. **ExecutionResult**: Encapsulates the output of a single test case run (actual output, simulated execution time, simulated memory used).

## 2. Design Patterns
1. **Strategy Pattern**: For fake language-specific execution adapters. `LanguageAdapter` interface has implementations like `FakePythonAdapter`, `FakeJavaAdapter`.
2. **Producer-Consumer / Queue**: For asynchronous processing of submissions. A thread-safe queue holds incoming submissions, and background Worker threads process them.
3. **State Machine**: To transition submission states (PENDING -> RUNNING -> FINAL_VERDICT) exactly once, rejecting duplicate updates.

## 3. Execution Flow (Simulation)
1. **Delegation**: Submissions are dequeued and passed to the appropriate `FakeLanguageAdapter`.
2. **Deterministic Simulation**: The adapter uses the submission's code (e.g., specific string patterns in test fixtures) to decide the verdict. It does NOT invoke `eval()`, `exec()`, compilers, or shells.
3. **Adapter-Reported Limits**: TLE and MLE are returned as deterministic string-matched simulated verdicts. They are not based on measuring real CPU/memory usage, as stdlib constraints do not provide a real security sandbox.
4. **Final Verdict Extraction**: The worker commits the first terminal verdict returned by the adapter. Subsequent updates for that submission ID are ignored.

## 4. External Sandbox Boundary
The real execution (if deployed to production) relies on a separately approved VM or container boundary. This boundary must provide hard isolation for:
- Filesystem (chroot, overlayfs)
- Network (airgapped, isolated namespaces)
- CPU/Memory (cgroups)
- Process (PID namespaces, ptrace limits)
Our trusted adapter simulation in this system explicitly mocks this boundary rather than attempting unproven isolation in the host process.
