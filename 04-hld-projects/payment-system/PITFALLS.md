# Payment System — Common Pitfalls

## Must-fix pitfalls

1. **No idempotency key enforcement for create/confirm/refund APIs.** Client retries are normal; without payload-hash replay semantics, the system can double-charge or return inconsistent responses.
2. **Treating gateway timeout as failure.** A timeout means the local system lacks evidence; mark the transaction unknown, poll the provider, and reconcile later.
3. **Updating balances without immutable ledger/event records.** Mutable rows are not enough for audit, dispute, replay, or settlement mismatch debugging.
4. **Missing split between synchronous client path and asynchronous settlement/webhook path.** Financial systems need quick user feedback and slower evidence repair.
5. **Ignoring duplicate/out-of-order webhook delivery.** Providers retry callbacks; the handler must verify signatures, dedupe event ids, and apply legal state transitions only.
6. **No fallback path when risk service is degraded.** Decide whether to fail closed, fail open for low-risk merchants, or route to manual review.

## Interview traps

- Saying "use a third-party gateway" as the whole design.
- Omitting refunds, partial captures, disputes, or reconciliation until prompted.
- Using a distributed transaction across the gateway boundary.
- Forgetting that webhook payloads are untrusted external input.
- Mixing accounting ledger, payment orchestration, and provider adapters into one service.

## How to avoid them
- Design around payment state machine transitions and terminal states.
- Persist every external interaction with request/response checksum for audit.
- Add periodic reconciliation jobs against gateway settlement files.
- Keep PCI-sensitive card handling behind tokenization/gateway boundaries.
