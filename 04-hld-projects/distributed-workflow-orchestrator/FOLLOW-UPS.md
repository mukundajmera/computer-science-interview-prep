# Distributed Workflow Orchestrator - Follow-Up Questions

## Follow-up questions

1.  **What happens if a workflow history grows to millions of events?**
    -   *Expected Answer:* Event histories cannot grow infinitely because the cost to transfer and replay them becomes prohibitive. We enforce a maximum event limit (e.g., 50k). To handle genuinely infinite workflows (like a cron job), the system must support a `Continue-As-New` primitive. The workflow yields its current logical state and the system spawns a fresh execution (with a new `run_id` and an empty history) starting from that state.

2.  **How do you prevent a "split-brain" where two workers are executing the same activity?**
    -   *Expected Answer:* The orchestrator acts as the single source of truth. When an activity task is dispatched, the orchestrator records a lease timeout in the database. Even if worker A hangs and worker B picks up a retried task, the orchestrator will only accept a `CompleteActivity` API call that includes the currently valid `task_token`. If worker A eventually wakes up and tries to complete the task, the orchestrator rejects it.

3.  **How are durable timers implemented?**
    -   *Expected Answer:* Timers are written to a database table, partitioned by expiration time. A background component (the "Timer queue processor") continuously polls or scans this table for expired timestamps. When a timer expires, it translates that row into a `TimerFired` event and pushes it to the corresponding workflow task queue to wake up the workflow.

4.  **If a workflow calls `sleep(30 days)`, does the worker block a thread for 30 days?**
    -   *Expected Answer:* No. The worker intercepts the `sleep` call, sends a `StartTimer` command to the orchestrator, and then *suspends the workflow execution* (the thread exits). The orchestrator persists the timer. 30 days later, the orchestrator fires the timer and dispatches a new workflow task. A worker (possibly a different one) picks it up, replays the history to rebuild the state, sees the timer has fired, and continues execution.

## Variants and extensions

-   **Multi-Region Failover:** How do you handle a total AWS region failure? (Requires async replication of the database and mechanisms to failover workflow executions to a secondary region, resolving split-brain using a global transaction coordinator).
-   **Signal and Query:** How can an external system interact with a running workflow? (Introduce `Signal` APIs to inject asynchronous events into a workflow's history, and `Query` APIs to synchronously ask a worker for the workflow's current in-memory state).

## Interviewer probes to prepare

-   "Walk me through the exact database transactions required when an activity worker successfully completes a task."
-   "What if the orchestrator crashes right after receiving a completion payload from a worker, but before enqueuing the next task?"
