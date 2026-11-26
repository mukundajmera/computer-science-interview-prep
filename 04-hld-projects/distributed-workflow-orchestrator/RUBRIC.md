# Distributed Workflow Orchestrator - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
| :--- | :--- | :--- |
| **Requirements & Scope** | 15% | Explicitly separates deterministic orchestration logic from non-deterministic activity logic. Identifies the need for exact-once execution semantics for activities. |
| **Core Architecture** | 25% | Articulates the Event Sourcing pattern clearly. Explains the separation of History management and Task Queue dispatching. |
| **Failure Handling** | 25% | Explains worker leases, timeouts, and heartbeat mechanisms for zombie worker eviction. Discusses Saga pattern for compensating actions. |
| **Scale & Storage** | 20% | Addresses the storage volume (TB/day) and the need to paginate/cap event histories to prevent bounded replay limits. Proposes a partitioned, strongly consistent database. |
| **Communication** | 15% | Structured presentation, clear separation of concerns, addresses tradeoffs without prompting. |

## Performance Bands

### 1-2: Weak
- Fails to grasp the difference between the orchestrator and the worker.
- Proposes a basic task queue (like RabbitMQ or Kafka) without addressing how multi-step state is durably maintained across failures.
- Cannot explain how to resume a workflow exactly where it crashed.

### 3: Okay
- Designs a state machine but struggles with the replay mechanics.
- Suggests checkpointing the entire program state (heap) instead of event sourcing.
- Handles retries but misses the nuance of activity heartbeats for long-running tasks.

### 4: Good
- Clearly articulates the Event Sourcing replay approach.
- Separates the History service from the Matching/Queue service.
- Understands long-polling for worker dispatch.
- Mentions Saga patterns for distributed rollbacks.

### 5: Strong
- Identifies the risk of unbounded history arrays and suggests pagination/limits.
- Discusses the need for strong consistency (transactions) between writing to the history table and enqueuing to the task queue.
- Proposes an efficient database partition key scheme (e.g., by `namespace_id` and `workflow_id`).
- Explains how durable timers work (scanning a partitioned database table).

## Cross-links
- [Problem Context](PROBLEM.md)
- [Design Document](DESIGN.md)
- [Common Pitfalls](PITFALLS.md)
