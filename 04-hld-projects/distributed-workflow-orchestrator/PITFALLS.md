# Distributed Workflow Orchestrator - Common Pitfalls

## 1. Misunderstanding "Where" the Code Runs
- **Failure Signal:** The candidate designs a system where the orchestrator itself executes the user's Java/Python/Go code.
- **Root Cause:** Treating the orchestrator as a Serverless compute platform (like AWS Lambda) instead of a control plane.
- **Mitigation:** Explicitly separate the Orchestrator (state machine, database, queues) from the Workers (user-hosted processes polling for tasks).

## 2. Using In-Memory Message Brokers (Kafka/RabbitMQ) for State
- **Failure Signal:** Storing workflow state or routing tasks using only a standard message broker.
- **Root Cause:** Underestimating the need for complex, transactional state transitions. If a worker completes an activity, the system must *transactionally* update the workflow history AND enqueue the next task.
- **Mitigation:** Propose a strongly consistent database (like CockroachDB or Cassandra with LWT) that backs both the history tables and the task queue tables.

## 3. Ignoring the Replay Limit Problem
- **Failure Signal:** Assuming event histories can grow infinitely.
- **Root Cause:** Event sourcing works well until the history gets so large that fetching it and replaying it takes longer than the task timeout.
- **Mitigation:** Implement a maximum history size limit (e.g., 50k events) and a mechanism to "Continue-As-New" (which takes the current logical state and starts a fresh workflow execution with a clean history).

## 4. Missing the Zombie Worker Problem
- **Failure Signal:** Relying solely on the overall workflow timeout (e.g., 1 hour) to handle crashes.
- **Root Cause:** If an activity takes 1 hour to timeout, a worker crash means the workflow is stalled for 1 hour before the orchestrator realizes it needs to re-assign the task.
- **Mitigation:** Introduce Activity Heartbeats. The worker must ping the orchestrator every `X` seconds; if a heartbeat is missed, the lease is revoked, and the task is immediately re-queued.

## 5. Non-Deterministic Replays
- **Failure Signal:** Failing to realize why `Math.random()` or `Date.now()` breaks the system.
- **Root Cause:** If a workflow executes a different code path on replay than it did originally, the orchestrator will see a command sequence mismatch and panic, halting the workflow.
- **Mitigation:** Emphasize that the orchestrator must provide deterministic APIs for random numbers and time, which are recorded in the event history and replayed exactly.
