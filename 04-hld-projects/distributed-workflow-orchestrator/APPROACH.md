# Distributed Workflow Orchestrator - Approach

## High-Level Strategy

The core challenge of a distributed workflow orchestrator is ensuring **durable execution**. If the process running a workflow crashes, the workflow must be able to resume exactly where it left off, without repeating side-effects or losing state.

We achieve this through **Event Sourcing**. Instead of constantly checkpointing the entire state of the JVM/V8 heap to a database (which is slow, platform-dependent, and fragile), the orchestrator persists a history of all significant events (e.g., `WorkflowExecutionStarted`, `ActivityTaskScheduled`, `ActivityTaskCompleted`). When a workflow worker picks up a task, it receives this event history, replays it through the deterministic workflow code to rebuild the in-memory state, and then continues execution until it hits the next blocking operation (like waiting for an activity or a timer).

### Key Abstractions

1. **Workflows:** The deterministic orchestration logic. Workflows cannot interact with the outside world directly (no network calls, no random numbers, no system clocks). They only communicate by scheduling activities or timers via the orchestrator.
2. **Activities:** Non-deterministic, side-effecting code (e.g., charging a credit card, sending an email). Activities are executed exactly once (if successful) or retried based on policies. Their results are recorded in the workflow history.
3. **Workers:** User-hosted processes that run the actual workflow and activity code. They poll the orchestrator for tasks.
4. **Task Queues:** The routing mechanism connecting the orchestrator's dispatch system to the worker fleets.

## Core Mechanisms

### 1. Deterministic Replay
Because workflows are deterministic, re-running the same code against the same event history guarantees the exact same sequence of API calls to the orchestrator. The orchestrator enforces this by verifying that the sequence of commands generated during replay exactly matches the existing history. Once the replay reaches the end of the history, the workflow is "caught up" and any new commands generated are processed as new events.

### 2. Task Dispatch and Queues
Workers long-poll the orchestrator on specific task queues. When the orchestrator determines a workflow or activity is ready to run, it enqueues a task.
- **Activity Task Queues:** For dispatching side-effecting tasks.
- **Workflow Task Queues:** For dispatching workflow execution tasks (which include the event history or a delta since the last run).

### 3. Worker Leases and Heartbeats
To handle worker crashes, tasks are dispatched with a lease (timeout). If a worker fails to complete an activity within the lease duration, the orchestrator re-enqueues the task. For long-running activities, workers emit periodic heartbeats to the orchestrator to extend their lease and prove they are still alive.

### 4. Durable Timers
Workflows often need to sleep for days or wait for external signals. The orchestrator stores these timers in a dedicated database table (e.g., partitioned by trigger time). A timer component continually scans for expired timers and pushes corresponding events (like `TimerFired`) into the workflow's task queue, waking it up.

### 5. Saga Compensation
For distributed transactions, the orchestrator supports the Saga pattern. If a workflow fails midway, it can execute a series of compensating activities to undo the previous steps. By structuring these compensations as a DAG and executing them in reverse order, the orchestrator ensures eventual consistency across microservices.

## Trade-off Considerations

- **Event Sourcing vs. State Checkpointing:** Event sourcing requires workflows to be strictly deterministic. State checkpointing allows non-deterministic code but requires complex serialization of the call stack and heap, which is hard to scale and language-dependent. We choose Event Sourcing for flexibility and performance.
- **Long-Polling vs. WebSockets:** WebSockets provide lower latency push but require persistent connection management and complex load balancing. Long-polling is simpler to scale, stateless at the edge, and sufficient for the latency requirements of most workflows. We use long-polling for worker task fetching.
- **Coarse Timeouts vs. Heartbeats:** Relying only on coarse task timeouts (e.g., 1 hour) means a crashed worker holds a lock for a long time. Activity heartbeats (e.g., every 15s) allow rapid detection of zombie workers and faster reassignment.
