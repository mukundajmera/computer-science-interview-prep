# Workflow Orchestration

Workflow orchestration coordinates multi-step business processes that must survive failures, retries, and long execution windows.

## What is it?

It is the pattern of managing ordered steps, durable state, retries, and compensating actions across multiple services.

## Why do we need it?

- Multi-step flows fail partially in real systems.
- In-process orchestration breaks on restart/deploy/crash.
- Long-running processes need durable progress and recovery points.

## Types/Approaches

### 1. In-Service Orchestration
- Simpler for small workflows.
- Limited resilience and operability as complexity grows.

### 2. Saga Orchestration
- Each step commits independently.
- Compensating steps roll back semantic effects on failure.

### 3. Durable Workflow Engines
- Persist workflow state/events.
- Support resume, retry policies, and versioned workflow definitions.

## How it works

1. Start workflow with idempotency key.
2. Persist initial state and step plan.
3. Execute step with retry policy.
4. Persist progress checkpoint.
5. On failure, run compensation chain.
6. Publish final success/failure event.

## When to use

- Checkout/order lifecycle, fulfillment pipelines, document processing, transcoding, onboarding flows.

## When NOT to use

- Single-step operations where plain transaction is enough.
- Tiny workflows where orchestration overhead outweighs value.

## Trade-offs

| Model | Benefit | Cost |
|---|---|---|
| Inline orchestration | Fast to implement | Fragile recovery |
| Saga | Good distributed fit | Compensation complexity |
| Durable engine | Strong reliability/visibility | Infra and operational overhead |

## Requirements and constraints

- All side-effecting steps must be idempotent.
- Compensation semantics must be explicit and testable.
- Store workflow progress durably before advancing.
- Versioning strategy must protect in-flight workflows.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|---|---|---|
| Reliability model | Clear retry + compensation + checkpointing | Best-effort retries only |
| State handling | Durable progress with resume path | In-memory step tracking |
| Evolution | Workflow versioning/migration plan | Ignores in-flight upgrades |
| Scope control | Chooses orchestration only when justified | Uses workflow engine everywhere |

## Common pitfalls

- Retrying non-idempotent steps blindly.
- Missing compensation for external side effects.
- No durable state checkpointing.
- Changing workflow definitions without migration strategy.

## Follow-up questions

1. How do you recover after orchestrator crash mid-step?
2. Which steps are safe to retry automatically?
3. How do you version workflows with in-flight instances?
4. What is your audit/event model for workflow execution?
5. When would you choose choreography over orchestration?

## Variants and extensions

- Human-in-the-loop approval step.
- Timeout-aware compensation lanes.
- Priority queues for urgent workflows.
- Region-local orchestration with global audit stream.

## Related concepts

- [Idempotency](../idempotency/THEORY.md)
- [Distributed Transactions](../distributed-transactions/THEORY.md)
- [Message Queues](../message-queues/THEORY.md)
- [Microservices Communication](../microservices-communication/THEORY.md)
- [Pattern Selection for HLD Interviews](../pattern-selection/THEORY.md)
- [E-commerce Backend HLD](../../04-hld-projects/ecommerce-backend/)
- [Video Streaming HLD](../../04-hld-projects/video-streaming/)

---

## Source 16 Integration: Price Alert Workflow

Price tracking subscriptions map naturally to durable orchestration: ingest change -> evaluate threshold -> schedule notification -> record delivery outcome with idempotent transitions.
