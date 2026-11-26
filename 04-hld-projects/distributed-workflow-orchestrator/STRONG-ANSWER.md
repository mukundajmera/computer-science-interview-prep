# Distributed Workflow Orchestrator - Strong Answer

## 1. Structure the Approach

A strong candidate will immediately clarify that the system consists of a "Control Plane" (the orchestrator) and a "Data Plane" (the user's worker processes).

> **Say:** "To build a distributed workflow orchestrator, I want to strictly separate the orchestration state machine from the actual code execution. The orchestrator will be a set of highly available services managing state in a database, while the user's workflow and activity code will run on external worker nodes that long-poll the orchestrator for tasks."

## 2. Define the State Storage Strategy

The core technical decision is how to durably pause and resume code.

> **Say:** "Instead of trying to checkpoint the entire memory heap of the worker process, which is fragile, I'll use Event Sourcing. Every time the workflow schedules an activity or starts a timer, the orchestrator appends that event to a history table. When a worker picks up a task after a crash, it receives this history, replays it through the deterministic workflow code to rebuild the state, and then continues."

## 3. Detail the Dispatch Mechanism

Explain how tasks move from the orchestrator to the workers.

> **Say:** "For dispatching, I'll use a Matching Service backed by a `task_queues` database table. Workers will long-poll this service. When a workflow generates a command like `ScheduleActivity`, the History Service will transactionally write the `ActivityScheduled` event to the history table AND write a task row into the `task_queues` table. This prevents split-brain where an event is recorded but the task is never dispatched."

## 4. Address Failure Modes and Edge Cases

Demonstrate operational awareness by handling worker crashes.

> **Say:** "To handle worker failures, I will implement task leases. When the Matching Service hands a task to a worker, it records a timeout. For long-running activities, the worker must send periodic heartbeats to renew the lease. If the lease expires—meaning the worker crashed or disconnected—the Matching Service simply re-enqueues the task for another worker to pick up."

## 5. Address Scale and Storage

Connect the design back to the provided constraints (e.g., 6.48 TB/day).

> **Say:** "Because we are generating terabytes of event history daily, we need a horizontally scalable database like CockroachDB or Cassandra, partitioned by `namespace_id` and `workflow_id`. Additionally, event histories cannot grow infinitely because the replay cost becomes too high. I'll enforce a maximum history limit and provide a `Continue-As-New` primitive, allowing a workflow to yield its current state and start fresh with an empty history."
