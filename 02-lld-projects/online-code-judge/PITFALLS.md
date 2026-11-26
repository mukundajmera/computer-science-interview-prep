# Pitfalls: Online Code Judge

1. **Running all test cases on WA**: A common mistake is executing all 100 test cases even if the first one fails. The judge should short-circuit and return `WA` or `TLE` immediately upon the first failure to save resources.
2. **Synchronous Execution**: Blocking the HTTP request/caller thread while compiling and executing code. Submissions must be handled asynchronously.
3. **Deadlocks in Queue**: If the queue blocks forever and background workers crash, submissions hang in `PENDING`. Graceful error handling in workers is crucial.
4. **Ignoring Sandbox/Security Isolation Boundaries**: Assuming stdlib timeouts/resource labels are a security sandbox. Candidates must understand that MLE/TLE are adapter-reported simulations here, not unproven isolation. Real isolation requires a separately approved VM/container boundary with filesystem/network/CPU/memory/output/process controls.
