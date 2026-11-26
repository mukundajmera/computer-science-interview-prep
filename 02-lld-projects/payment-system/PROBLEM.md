# Payment System

## Problem Statement
Design low-level payment orchestration components for intent creation, confirmation, and reconciliation with progressive Java/Python versions.

## Requirements and constraints

### Functional requirements
1. Create payment intents with idempotency key support.
2. Execute state-machine transitions (`CREATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED`).
3. Persist immutable transaction records for audit and reconciliation.
4. Process asynchronous gateway callbacks safely (duplicate/out-of-order tolerant).

### Non-functional requirements
- Deterministic tests with fake gateway adapter.
- No external network/payment dependencies.
- Thread-safe state updates in `v3`.
- Standard-library-only implementation.

## Version roadmap
- **v1-basic:** intent + transaction domain core.
- **v2-extended:** gateway strategy adapter, retry and risk policy hooks.
- **v3-optimized:** concurrent processing queue, recovery checkpoints, reconciliation abstraction.

## Related content
- [HLD Payment System](../../04-hld-projects/payment-system/)
- [Workflow Orchestration and Sagas](../../03-hld-concepts/workflow-orchestration/THEORY.md)
