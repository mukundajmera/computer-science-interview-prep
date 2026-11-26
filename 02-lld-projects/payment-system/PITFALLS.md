# Payment System - Common Pitfalls

## Common pitfalls
1. Treating gateway timeout as a terminal payment failure.
2. Updating payment status before validating the idempotency key and legal transition.
3. Relying on mutable current state without immutable transaction records for reconciliation.
4. Trusting callback order from gateway providers.
5. Mixing API, orchestration, gateway routing, risk policy, and persistence in one class.

## Why these fail interviews
- They lose money-state accuracy during duplicate requests or uncertain gateway outcomes.
- They make audit and reconciliation impossible to explain.
- They hide retry and callback behavior inside untestable integration code.

## Mitigations
- Centralize transition guards for `CREATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, and `REFUNDED`.
- Record every external interaction before using it to drive reconciliation.
- Route gateway behavior through deterministic adapters and policy interfaces.
- Treat callback handling as deduplication plus ordering validation, not a simple status overwrite.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Workflow orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
