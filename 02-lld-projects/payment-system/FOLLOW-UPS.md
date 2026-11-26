# Payment System - Follow-Up Questions

## Follow-up questions
1. How would you add partial capture support while preserving state-machine invariants?
2. What recovery logic is needed when the gateway outcome is unknown after a timeout?
3. How would you process duplicate or out-of-order callbacks without corrupting the intent state?
4. Which interfaces should become remote services in a distributed payment architecture?
5. How would you evolve API versions without breaking idempotency contracts?

## Variants and extensions
1. Tenant-specific gateway routing and risk policy hooks.
2. Authorization/capture separation with refund and dispute workflows.
3. Reconciliation batches that compare ledger records against gateway reports.
4. Outbox-backed event publication after payment state changes.

## Interviewer probes to prepare
- "What is the source of truth for payment state?"
- "How do you represent an uncertain gateway result?"
- "Where do idempotency and reconciliation intersect?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
