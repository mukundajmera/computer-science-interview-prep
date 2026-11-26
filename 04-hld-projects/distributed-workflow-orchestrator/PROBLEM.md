# Distributed Workflow Orchestrator - Problem Statement

## Problem Context

Modern microservice architectures often involve complex, long-running business processes that span multiple independent services. Examples include order fulfillment, user onboarding, or CI/CD pipelines. Managing these distributed transactions requires handling failures, retries, state persistence, and coordination across boundaries. A Distributed Workflow Orchestrator provides a reliable platform for defining, executing, and monitoring these stateful workflows.

Design a resilient Distributed Workflow Orchestrator (similar to Temporal, Cadence, or AWS Step Functions) that allows developers to write deterministic workflow logic and non-deterministic activity logic, providing durable execution guarantees even in the presence of node failures.

## Requirements

### Core User Value
- Provide a platform for developers to execute durable, stateful, long-running workflows without managing persistence or retries manually.

### Functional Requirements
- **FR1:** Support registering and starting deterministic workflow executions.
- **FR2:** Dispatch non-deterministic activities to worker pools.
- **FR3:** Maintain execution state durably using Event Sourcing (replay).
- **FR4:** Support long-running durable timers (e.g., sleep for days/months).
- **FR5:** Support automated Saga compensation DAGs (Try -> Compensate in reverse order) upon failure.
- **FR6:** Support activity task leases, heartbeat renewals, and zombie worker eviction.

### Non-Functional Requirements
- **Availability:** 99.99% for the control plane and dispatch mechanics.
- **Durability:** 99.9999% for workflow history and execution state.
- **Scalability:** Must support highly concurrent workflow executions and massive event histories.
- **Consistency:** Strong consistency for workflow state transitions and task queue dispatching to prevent duplicate executions.

## Scale and Constraints

### Traffic and Sizing
- **Workflow Starts:** 10,000 active workflow starts per second.
- **Activity Dispatches:** 100,000 activity dispatches per second.
- **Daily Volume:** 864 million workflow executions per day.
- **Event History Storage:** 6.48 TB per day (assuming average 7.5 KB event history per workflow).

### System Constraints
- **Separation of Concerns:** Deterministic workflow code vs. non-deterministic activity code.
- **Worker Execution:** User code runs on external worker nodes, not within the orchestrator itself.
- **Event Limits:** Individual workflow event histories must be paginated and have upper bounds (e.g., 50k events max) to prevent unbounded replay overhead.

## Out of Scope
- Workflow code compilation or container scheduling (focus is on orchestration, not compute provisioning).
- Complex UI dashboards (focus on the backend APIs and state management).
