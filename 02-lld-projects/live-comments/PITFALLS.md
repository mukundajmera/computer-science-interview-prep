# Live Comments - Common Pitfalls

## Common pitfalls
1. Treating ingest, fanout, replay, and session tracking as one mutable list.
2. Not assigning a deterministic sequence or timestamp for replay ordering.
3. Dropping reconnect state and forcing clients to miss comments after disconnects.
4. Replaying unbounded history instead of a bounded window.
5. Ignoring duplicate comment submissions when clients retry.

## Why these fail interviews
- They conflict with the documented fanout, replay, and reconnect responsibilities.
- They make repeated requests and reconnects non-deterministic.
- They hide the cost of low-latency fanout and replay storage.

## Mitigations
- Keep ingress validation separate from fanout delivery.
- Store replayable comment records with stable ordering.
- Track live sessions and last-seen positions explicitly.
- Use idempotency keys for v3 comment mutation retries.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
